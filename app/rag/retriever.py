from __future__ import annotations
from typing import List, Dict, Any
from .embeddings import EmbeddingModel
from .vector_store import ChromaVectorStore
from .config import settings
import logging
import math
import numpy as _np

logger = logging.getLogger("app.rag.retriever")


class Retriever:
    def __init__(self, embedding_model: EmbeddingModel, vector_store: ChromaVectorStore):
        self.emb = embedding_model
        self.vs = vector_store

    def retrieve(self, query: str, top_k: int | None = None) -> List[Dict[str, Any]]:
        top_k = top_k or settings.TOP_K
        # retrieve a larger candidate pool for reranking
        candidate_k = max(1, (top_k or settings.TOP_K) * settings.RAG_RERANK_TOP_K_FACTOR)
        q_emb = self.emb.embed_query(query)
        results = self.vs.similarity_search(q_emb, top_k=candidate_k)
        # Convert returned score to a normalized similarity in [0,1].
        for r in results:
            s = r.get("score", None)
            if s is None:
                r["similarity"] = 0.0
            else:
                # If score is in [-1,1] treat it as cosine similarity
                if isinstance(s, (int, float)) and -1.1 <= s <= 1.1:
                    # normalize cosine [-1,1] -> [0,1]
                    r["similarity"] = float((float(s) + 1.0) / 2.0)
                else:
                    # fallback: convert distance to similarity
                    r["similarity"] = 1.0 / (1.0 + float(s))

        # dynamic thresholding relative to top similarity
        sims = [r.get("similarity", 0.0) for r in results]
        if not sims:
            logger.info("Retriever: no similarity scores returned")
            return []
        max_sim = max(sims)
        # dynamic floor based on max_sim but not below configured threshold
        dynamic_thresh = max(settings.RAG_SIMILARITY_THRESHOLD, 0.75 * max_sim)
        filtered = [r for r in results if r.get("similarity", 0.0) >= dynamic_thresh]
        if not filtered:
            logger.info("Retriever: no chunks above similarity threshold (dynamic %.3f)", dynamic_thresh)
            return []

        # Optional reranking using cross-encoder if enabled
        if settings.RAG_RERANK_ENABLED and settings.RAG_RERANKER_MODEL:
            try:
                from sentence_transformers import CrossEncoder  # type: ignore
                reranker = CrossEncoder(settings.RAG_RERANKER_MODEL)
                pairs = [(query, r["text"]) for r in filtered]
                scores = reranker.predict(pairs)
                # attach rerank_score and sort
                for r, s in zip(filtered, scores):
                    r["rerank_score"] = float(s)
                filtered.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
            except Exception as exc:
                logger.warning("Reranker unavailable or failed: %s", exc)
                # leave filtered as-is

        # sort by similarity (or rerank_score if present)
        filtered.sort(key=lambda x: x.get("rerank_score", x.get("similarity", 0.0)), reverse=True)

        # Neighbor expansion: include adjacent chunk_index neighbors if present among results and similarity close
        final_set = []
        seen_ids = set()
        # build map for easy lookup based on (source, section_number, chunk_index)
        map_by_pos = {}
        for r in filtered:
            meta = r.get("metadata", {}) or {}
            key = (meta.get("source"), meta.get("section_number"), meta.get("chunk_index"))
            map_by_pos[key] = r

        for r in filtered:
            if r["id"] in seen_ids:
                continue
            final_set.append(r)
            seen_ids.add(r["id"])
            meta = r.get("metadata", {}) or {}
            try:
                idx = int(meta.get("chunk_index")) if meta.get("chunk_index") is not None else None
            except Exception:
                idx = None
            if idx is not None:
                for neighbor_idx in (idx - 1, idx + 1):
                    keyn = (meta.get("source"), meta.get("section_number"), neighbor_idx)
                    nr = map_by_pos.get(keyn)
                    if nr and nr["id"] not in seen_ids:
                        # include neighbor if its similarity is not too far from this chunk
                        if nr.get("similarity", 0.0) >= max(0.0, r.get("similarity", 0.0) * 0.75):
                            final_set.append(nr)
                            seen_ids.add(nr["id"])

        # trim to requested top_k
        final = final_set[: top_k or settings.TOP_K]
        logger.info("Retriever found %d results for query after filtering", len(final))
        return final

