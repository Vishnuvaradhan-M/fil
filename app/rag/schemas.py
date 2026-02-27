from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: Optional[int] = None


class Chunk(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]
    score: Optional[float] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    retrieved_chunks: List[Chunk]
    confidence: float = Field(0.0)
    notes: Optional[str] = None


class UploadResponse(BaseModel):
    ingested_chunks: int

