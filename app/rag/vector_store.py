from __future__ import annotations
from typing import List, Dict, Any
import logging
import os
import json
from .config import settings
logger = logging.getLogger("app.rag.vector_store")


class ChromaVectorStore:
    """
    Vector store wrapper that uses chromadb when available, otherwise falls back
    to a simple in-memory vector store. This allows the backend to remain functional
    even if chromadb or its native dependencies are not installed.
    """

    def __init__(self, persist_directory: str = None, collection_name: str = None):
        self._use_chroma = False
        # shared global in-memory store so multiple ChromaVectorStore instances
        # (created across requests) see the same documents when chromadb is unavailable.
        if not hasattr(ChromaVectorStore, "_global_in_memory"):
            ChromaVectorStore._global_in_memory: List[Dict[str, Any]] = []
        self._in_memory = ChromaVectorStore._global_in_memory
        persist_directory = persist_directory or settings.CHROMA_PERSIST_DIR
        collection_name = collection_name or settings.COLLECTION_NAME

        try:
            import chromadb  # type: ignore
            from chromadb.config import Settings  # type: ignore

            logger.info("Initializing ChromaDB at %s (collection=%s)", persist_directory, collection_name)
            self.client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist_directory))
            self.collection = self._get_or_create_collection(collection_name)
            self._use_chroma = True
        except Exception as exc:
            # Fallback to in-memory store with warning
            logger.warning("chromadb unavailable, falling back to in-memory vector store: %s", exc)
            self._use_chroma = False
            # ensure persist dir exists
            try:
                os.makedirs(persist_directory, exist_ok=True)
            except Exception:
                pass
            # file to persist in-memory documents across processes
            self._persist_file = os.path.join(persist_directory, f"{collection_name}_backup.jsonl")
            # load any existing persisted docs into global memory
            try:
                if os.path.exists(self._persist_file):
                    with open(self._persist_file, "r", encoding="utf-8") as fh:
                        for line in fh:
                            try:
                                doc = json.loads(line.strip())
                                # avoid duplicates by id
                                if not any(d.get("id") == doc.get("id") for d in self._in_memory):
                                    self._in_memory.append(doc)
                            except Exception:
                                continue
            except Exception:
                logger.exception("Failed to load persisted in-memory vector store")

    def _get_or_create_collection(self, name: str):
        try:
            return self.client.get_collection(name)
        except Exception:
            return self.client.create_collection(name)

    def add_documents(self, docs: List[Dict[str, Any]]):
        if self._use_chroma:
            ids = [d["id"] for d in docs]
            texts = [d["text"] for d in docs]
            metadatas = [d.get("metadata", {}) for d in docs]
            embeddings = [d.get("embedding") for d in docs] if docs and "embedding" in docs[0] else None
            if embeddings:
                self.collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
            else:
                self.collection.add(ids=ids, documents=texts, metadatas=metadatas)
            try:
                self.client.persist()
            except Exception:
                logger.exception("Failed to persist ChromaDB client state")
            logger.info("Added %d documents to ChromaDB", len(docs))
        else:
            # store in-memory
            added = 0
            for d in docs:
                if not any(existing.get("id") == d.get("id") for existing in self._in_memory):
                    self._in_memory.append(d)
                    added += 1
            # persist to disk so other processes can read them
            try:
                with open(self._persist_file, "a", encoding="utf-8") as fh:
                    for d in docs:
                        fh.write(json.dumps(d, ensure_ascii=False) + "\n")
            except Exception:
                logger.exception("Failed to persist in-memory docs to file")
            logger.info("Added %d documents to in-memory vector store (persisted)", added)

    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        if self._use_chroma:
            results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k, include=["metadatas", "documents", "distances", "ids"])
            out = []
            docs = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            ids = results.get("ids", [[]])[0]
            for _id, doc, meta, dist in zip(ids, docs, metadatas, distances):
                out.append({"id": _id, "text": doc, "metadata": meta, "score": float(dist)})
            out.sort(key=lambda x: x["score"])
            return out
        # in-memory similarity search (assumes embeddings are stored on docs)
        try:
            import numpy as np
        except Exception:
            raise RuntimeError("numpy is required for in-memory similarity search")
        if not self._in_memory:
            return []
        # build matrix
        ids = []
        texts = []
        metadatas = []
        embs = []
        for d in self._in_memory:
            if "embedding" not in d:
                continue
            ids.append(d["id"])
            texts.append(d["text"])
            metadatas.append(d.get("metadata", {}))
            embs.append(np.array(d["embedding"], dtype=float))
        if not embs:
            return []
        mat = np.vstack(embs)
        q = np.array(query_embedding, dtype=float)
        # compute cosine similarities (normalize embeddings)
        # avoid division by zero
        mat_norm = mat / (np.linalg.norm(mat, axis=1, keepdims=True) + 1e-12)
        q_norm = q / (np.linalg.norm(q) + 1e-12)
        sims = mat_norm.dot(q_norm)
        # get top indices by descending similarity
        idx = np.argsort(-sims)[:top_k]
        out = []
        for i in idx:
            out.append({"id": ids[int(i)], "text": texts[int(i)], "metadata": metadatas[int(i)], "score": float(sims[int(i)])})
        return out

