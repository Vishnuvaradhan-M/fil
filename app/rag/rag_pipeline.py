from __future__ import annotations
from typing import List, Dict, Any
from .retriever import Retriever
from .embeddings import EmbeddingModel
from .vector_store import ChromaVectorStore
from .config import settings
import logging

logger = logging.getLogger("app.rag.pipeline")


class RAGPipeline:
    def __init__(self, emb_model: EmbeddingModel | None = None, vector_store: ChromaVectorStore | None = None, generator: object | None = None):
        # Do not eagerly instantiate the Generator since groq may be unavailable.
        self.emb_model = emb_model or EmbeddingModel.get_instance(settings.EMBEDDING_MODEL_NAME)
        self.vector_store = vector_store or ChromaVectorStore(settings.CHROMA_PERSIST_DIR, settings.COLLECTION_NAME)
        self.retriever = Retriever(self.emb_model, self.vector_store)
        self._generator = generator  # may be None or a Generator-like instance

    def _format_context(self, chunks: List[Dict[str, Any]]) -> str:
        parts = []
        for c in chunks:
            meta = c.get("metadata", {}) or {}
            source = meta.get("source", "unknown")
            section_title = meta.get("section_title", "")
            section_number = meta.get("section_number", "")
            parts.append(f"Document: {source}\nSection: {section_title or section_number}\n--------------------------------\n{c.get('text','')}\n")
        context = "\n".join(parts)
        # truncate if too long (character-based fallback)
        if len(context) > settings.MAX_CONTEXT_TOKENS * 4:
            context = context[: settings.MAX_CONTEXT_TOKENS * 4]
        return context

    def run(self, query: str, top_k: int | None = None) -> Dict[str, Any]:
        try:
            results = self.retriever.retrieve(query, top_k=top_k)
        except Exception as exc:
            logger.exception("RAGPipeline: retriever failure: %s", exc)
            return {
                "answer": "The provided documents do not contain sufficient information.",
                "sources": [],
                "retrieved_chunks": [],
                "confidence": 0.0,
                "notes": "retriever error",
            }

        # If retrieval returned no candidates above threshold, immediately refuse.
        if not results:
            logger.info("RAGPipeline: no retrieval candidates; returning insufficient information")
            return {
                "answer": "I do not have enough information from the provided documents.",
                "sources": [],
                "retrieved_chunks": [],
                "confidence": 0.0,
                "notes": "no retrieved chunks above similarity threshold",
            }

        # deduplicate by text while keeping highest-similarity first
        try:
            seen_texts = set()
            dedup: List[Dict[str, Any]] = []
            for r in results:
                t = (r.get("text") or "").strip()
                if not t:
                    continue
                if t in seen_texts:
                    continue
                seen_texts.add(t)
                dedup.append(r)
            # ensure sorted by similarity descending and limit
            dedup.sort(key=lambda x: x.get("similarity", 0.0), reverse=True)
            dedup = dedup[: top_k or settings.TOP_K]
        except Exception as exc:
            logger.exception("RAGPipeline: dedup/trim failure: %s", exc)
            return {
                "answer": "The provided documents do not contain sufficient information.",
                "sources": [],
                "retrieved_chunks": [],
                "confidence": 0.0,
                "notes": "deduplication error",
            }

        context = self._format_context(dedup)
        # Build sources and trimmed_chunks before generation (needed by extractive_fallback)
        seen_sources = set()
        sources: List[Dict[str, Any]] = []
        for r in dedup:
            meta = r.get("metadata", {}) or {}
            src = meta.get("source", "unknown")
            if src in seen_sources:
                continue
            seen_sources.add(src)
            sources.append({"source": src, "score": r.get("similarity") or r.get("score")})
        trimmed_chunks: List[Dict[str, Any]] = []
        for r in dedup:
            trimmed_text = (r.get("text") or "").strip()
            if len(trimmed_text) > 1200:
                trimmed_text = trimmed_text[:1200] + "..."
            trimmed_chunks.append({"id": r.get("id"), "text": trimmed_text, "metadata": r.get("metadata", {}), "score": r.get("similarity") or r.get("score")})

        # Lazily instantiate generator to avoid hard dependency at import/startup.
        answer = ""
        extraction_fallback_used = False
        def extractive_fallback():
            # reuse extractive fallback logic: pick top sentences matching query terms
            import string
            raw_terms = [t.lower().strip(string.punctuation) for t in query.split() if len(t) > 1]
            stopwords = {
                "the", "and", "for", "with", "that", "this", "from", "are", "was", "were", "have", "has", "had", "which",
                "what", "when", "where", "who", "whom", "why", "how", "a", "an", "in", "on", "at", "by", "to", "of", "is",
            }
            q_terms = [t for t in raw_terms if t not in stopwords]
            if not q_terms:
                q_terms = [query.lower().strip()]
            scored_sentences = []
            min_overlap = max(1, settings.RAG_VERIFICATION_MIN_OVERLAP)
            for ch in trimmed_chunks:
                text = ch.get("text", "")
                sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
                chunk_score = ch.get("score") or 0.0
                for s in sentences:
                    s_norm = s.lower()
                    match_count = sum(1 for t in q_terms if t and t in s_norm)
                    if match_count < min_overlap and not all(t in s_norm for t in q_terms):
                        continue
                    scored_sentences.append((match_count, float(chunk_score or 0.0), s.strip()))
            scored_sentences.sort(key=lambda x: (x[0], x[1]), reverse=True)
            extracted = []
            seen_sents = set()
            for match_count, cscore, sent in scored_sentences:
                if sent in seen_sents:
                    continue
                seen_sents.add(sent)
                s_out = sent if len(sent) <= 800 else sent[:800] + "..."
                extracted.append(s_out + ".")
                if len(extracted) >= 3:
                    break
            if not extracted and trimmed_chunks:
                extracted = [trimmed_chunks[0]["text"][:600] + ("..." if len(trimmed_chunks[0]["text"]) > 600 else "")]
            return " ".join(extracted) if extracted else "I do not have enough information from the provided documents."

        try:
            if self._generator is None:
                try:
                    from .generator import Generator  # lazy import
                    self._generator = Generator()
                except Exception as exc:
                    logger.warning("Generator unavailable: %s", exc)
                    self._generator = None
                    # fall through to extractive fallback
            if self._generator and getattr(self._generator, "available", False):
                try:
                    answer = self._generator.generate(context, query, max_tokens=512)
                except Exception as exc:
                    logger.exception("Generation error: %s", exc)
                    # fall back to extractive
                    answer = extractive_fallback()
                    extraction_fallback_used = True
            else:
                # generator not available: use extractive fallback
                answer = extractive_fallback()
                extraction_fallback_used = True
        except Exception as exc:
            logger.exception("Unexpected error during generation: %s", exc)
            answer = extractive_fallback()
            extraction_fallback_used = True
        # sources and trimmed_chunks already built above
        # COPY-PASTE CHECK: if generated answer would later be >70% contiguous with any chunk, we will instruct regeneration
        # (This check happens after generation below.)
        # If generation failed or is unavailable, produce a safe extractive answer from retrieved chunks
        low_confidence_markers = (
            "RAG generation unavailable",
            "RAG generation failed",
            "generator dependency not installed",
            "generator unavailable",
        )
        used_generator = not any(marker in (answer or "") for marker in low_confidence_markers)

        if not used_generator:
            # extract best-matching sentences from retrieved chunks with stricter matching rules
            import string

            raw_terms = [t.lower().strip(string.punctuation) for t in query.split() if len(t) > 1]
            stopwords = {
                "the", "and", "for", "with", "that", "this", "from", "are", "was", "were", "have", "has", "had", "which",
                "what", "when", "where", "who", "whom", "why", "how", "a", "an", "in", "on", "at", "by", "to", "of", "is",
            }
            q_terms = [t for t in raw_terms if t not in stopwords]
            if not q_terms:
                # fallback to whole query if stripping produced nothing
                q_terms = [query.lower().strip()]

            scored_sentences: List[tuple[int, float, str]] = []
            min_overlap = max(1, settings.RAG_VERIFICATION_MIN_OVERLAP)
            for ch in trimmed_chunks:
                text = ch.get("text", "")
                sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
                chunk_score = ch.get("score") or 0.0
                for s in sentences:
                    s_norm = s.lower()
                    match_count = sum(1 for t in q_terms if t and t in s_norm)
                    # require at least min_overlap OR all query terms present
                    if match_count < min_overlap and not all(t in s_norm for t in q_terms):
                        continue
                    scored_sentences.append((match_count, float(chunk_score or 0.0), s.strip()))

            # sort by (match_count desc, chunk_score desc)
            scored_sentences.sort(key=lambda x: (x[0], x[1]), reverse=True)
            extracted: List[str] = []
            seen_sents = set()
            for match_count, cscore, sent in scored_sentences:
                if sent in seen_sents:
                    continue
                seen_sents.add(sent)
                s_out = sent if len(sent) <= 800 else sent[:800] + "..."
                extracted.append(s_out + ".")
                if len(extracted) >= 3:
                    break
            # Only accept extracted answers if they meet strict match criteria
            if not extracted:
                answer = "I do not have enough information from the provided documents."
            else:
                answer = " ".join(extracted)
        # If generation was used, perform grounding verification
        notes = None
        retrieval_conf = 0.0
        if sources:
            retrieval_conf = max((s.get("score") or 0.0) for s in sources)

        verification_fraction = 0.0
        if used_generator:
            # Semantic validation: embed generated answer and compare to retrieved chunk embeddings
            try:
                ans_emb = self.emb_model.embed_query(answer)
                # compute chunk embeddings
                chunk_texts = [c.get("text", "") for c in trimmed_chunks]
                chunk_embs = self.emb_model.embed_documents(chunk_texts)
                # compute cosine similarities
                import numpy as np, math
                qv = np.array(ans_emb, dtype=float)
                qv = qv / (np.linalg.norm(qv) + 1e-12)
                sims = []
                for ce in chunk_embs:
                    cv = np.array(ce, dtype=float)
                    cv = cv / (np.linalg.norm(cv) + 1e-12)
                    sims.append(float(np.dot(qv, cv)))
                # sims in [-1,1] map to [0,1]
                sims_norm = [ (s + 1.0) / 2.0 for s in sims ] if sims else [0.0]
                semantic_alignment = max(sims_norm) if sims_norm else 0.0
            except Exception as exc:
                logger.warning("Semantic validation failed: %s", exc)
                semantic_alignment = 0.0

            # avg retrieval similarity
            avg_similarity = 0.0
            try:
                avg_similarity = float(sum((r.get("similarity") or 0.0) for r in dedup) / max(1, len(dedup)))
            except Exception:
                avg_similarity = 0.0

            rerank_avg = 0.0
            rerank_vals = [r.get("rerank_score") for r in dedup if r.get("rerank_score") is not None]
            if rerank_vals:
                # normalize reranker scores to [0,1] conservatively
                minv = min(rerank_vals)
                maxv = max(rerank_vals)
                if maxv > minv:
                    rerank_avg = float(sum((v - minv) / (maxv - minv) for v in rerank_vals) / len(rerank_vals))
                else:
                    rerank_avg = float(rerank_vals[0])

            # composite confidence: use retrieval + semantic alignment weights
            final_confidence = avg_similarity * float(settings.RAG_CONF_RETRIEVAL_WEIGHT) + semantic_alignment * float(settings.RAG_CONF_VERIFICATION_WEIGHT)

            # require semantic alignment threshold
            if semantic_alignment < 0.6:
                notes = "generation rejected: semantic alignment below threshold"
                # fallback to extractive answer (reuse earlier extraction logic)
                q_terms = [t.lower().strip() for t in query.split() if len(t) > 2]
                extracted: List[str] = []
                for ch in trimmed_chunks:
                    text = ch.get("text", "")
                    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
                    for s in sentences:
                        s_l = s.lower()
                        if any(t in s_l for t in q_terms):
                            extracted.append(s.strip() + ".")
                            if len(extracted) >= 3:
                                break
                    if len(extracted) >= 3:
                        break
                if not extracted and trimmed_chunks:
                    extracted = [trimmed_chunks[0]["text"][:600] + ("..." if len(trimmed_chunks[0]["text"]) > 600 else "")]
                answer = " ".join(extracted) if extracted else "The provided documents do not contain sufficient information."
        else:
            # no generator used: compute confidence based on retrieval only
            final_confidence = float(retrieval_conf) * float(settings.RAG_CONF_RETRIEVAL_WEIGHT)
        # COPY-PASTE CHECK: detect large contiguous matches (>70% of answer length)
        try:
            def has_large_contiguous_match(ans: str, text: str, ratio: float = 0.7) -> bool:
                if not ans or not text:
                    return False
                thresh = max(20, int(len(ans) * ratio))
                if thresh <= 0 or len(ans) < thresh:
                    return False
                for i in range(0, len(ans) - thresh + 1):
                    sub = ans[i:i+thresh]
                    if sub in text:
                        return True
                return False

            regenerate = False
            for ch in trimmed_chunks:
                if has_large_contiguous_match(answer, ch.get("text", "")):
                    regenerate = True
                    break
            if regenerate and self._generator and getattr(self._generator, "available", False):
                regen_query = query + "\n\nPlease rewrite concisely in the structured format requested earlier without copying verbatim from the context. Use your own words and synthesize key points."
                try:
                    regen_answer = self._generator.generate(context, regen_query, max_tokens=512)
                    if regen_answer and not any(has_large_contiguous_match(regen_answer, c.get("text","")) for c in trimmed_chunks):
                        answer = regen_answer
                        # recompute semantic alignment and confidence
                        try:
                            ans_emb = self.emb_model.embed_query(answer)
                            chunk_texts = [c.get("text", "") for c in trimmed_chunks]
                            chunk_embs = self.emb_model.embed_documents(chunk_texts)
                            import numpy as np
                            qv = np.array(ans_emb, dtype=float)
                            qv = qv / (np.linalg.norm(qv) + 1e-12)
                            sims = []
                            for ce in chunk_embs:
                                cv = np.array(ce, dtype=float)
                                cv = cv / (np.linalg.norm(cv) + 1e-12)
                                sims.append(float(np.dot(qv, cv)))
                            sims_norm = [ (s + 1.0) / 2.0 for s in sims ] if sims else [0.0]
                            semantic_alignment = max(sims_norm) if sims_norm else 0.0
                            avg_similarity = float(sum((r.get("similarity") or 0.0) for r in dedup) / max(1, len(dedup)))
                            final_confidence = avg_similarity * float(settings.RAG_CONF_RETRIEVAL_WEIGHT) + semantic_alignment * float(settings.RAG_CONF_VERIFICATION_WEIGHT)
                            notes = (notes or "") + " Regenerated to reduce verbatim copying."
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass

        return {
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": trimmed_chunks,
            "confidence": float(final_confidence),
            "notes": notes,
        }

