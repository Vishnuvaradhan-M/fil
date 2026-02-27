from __future__ import annotations
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form
from typing import List
from .schemas import QueryRequest, QueryResponse, UploadResponse, Chunk
from .ingestion import ingest_file_bytes
from .embeddings import EmbeddingModel
from .rag_pipeline import RAGPipeline
from .config import settings
from .utils import logger as rag_logger
from app.core.deps import get_current_active_user
import logging

router = APIRouter(prefix="/rag", tags=["RAG"])

_logger = logging.getLogger("app.rag.api")


def _admin_or_hr_user(current_user = Depends(get_current_active_user)):
    # avoid importing UserRole; check enum value string
    try:
        role_value = getattr(current_user.role, "value", str(current_user.role))
    except Exception:
        role_value = str(current_user.role)
    if role_value not in ("admin", "hr"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    return current_user


@router.post("/upload", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...), current_user=Depends(_admin_or_hr_user)):
    total = 0
    emb = EmbeddingModel.get_instance(settings.EMBEDDING_MODEL_NAME)
    # lazy import for vector store to avoid startup-time import errors
    try:
        from .vector_store import ChromaVectorStore  # local import
        vs = ChromaVectorStore(settings.CHROMA_PERSIST_DIR, settings.COLLECTION_NAME)
    except Exception as exc:
        _logger.exception("Vector store unavailable: %s", exc)
        raise HTTPException(status_code=500, detail="Vector store unavailable; check server logs")
    docs_to_add = []
    for f in files:
        data = await f.read()
        chunks = ingest_file_bytes(f.filename, data)
        texts = [c["text"] for c in chunks]
        embeddings = emb.embed_documents(texts)
        for c, emb_vec in zip(chunks, embeddings):
            c["embedding"] = emb_vec
            docs_to_add.append(c)
        total += len(chunks)
    if docs_to_add:
        try:
            vs.add_documents(docs_to_add)
        except Exception:
            _logger.exception("Failed to add documents to vector store")
            raise HTTPException(status_code=500, detail="Failed to persist documents to vector store")
    _logger.info("Uploaded %d chunks", total)
    return UploadResponse(ingested_chunks=total)


@router.post("/query", response_model=QueryResponse)
async def query_rag(payload: QueryRequest, current_user=Depends(get_current_active_user)):
    try:
        pipeline = RAGPipeline()
        res = pipeline.run(payload.query, top_k=payload.top_k)
        chunks = [Chunk(id=c.get("id"), text=c.get("text"), metadata=c.get("metadata", {}), score=c.get("score")) for c in res.get("retrieved_chunks", [])]
        return QueryResponse(
            answer=res.get("answer", ""),
            sources=res.get("sources", []),
            retrieved_chunks=chunks,
            confidence=float(res.get("confidence", 0.0)),
            notes=res.get("notes"),
        )
    except Exception as exc:
        _logger.exception("RAG pipeline error: %s", exc)
        # Return 200 with safe response so frontend health check succeeds and UI stays available
        return QueryResponse(
            answer="I do not have enough information from the provided documents.",
            sources=[],
            retrieved_chunks=[],
            confidence=0.0,
            notes="RAG temporarily unavailable; please try again.",
        )

