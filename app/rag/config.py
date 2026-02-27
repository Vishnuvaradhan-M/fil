from __future__ import annotations
import os
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class RAGSettings(BaseSettings):
    CHROMA_PERSIST_DIR: str = Field("chroma_persist", env="CHROMA_PERSIST_DIR")
    COLLECTION_NAME: str = Field("hospital_knowledge", env="COLLECTION_NAME")
    EMBEDDING_MODEL_NAME: str = Field("all-MiniLM-L6-v2", env="EMBEDDING_MODEL_NAME")
    GROQ_MODEL: str = Field("gpt-oss-20b", env="GROQ_MODEL")
    TOP_K: int = Field(5, env="RAG_TOP_K")
    CHUNK_SIZE: int = Field(1000, env="RAG_CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(200, env="RAG_CHUNK_OVERLAP")
    MAX_CONTEXT_TOKENS: int = Field(3000, env="RAG_MAX_CONTEXT_TOKENS")
    GROQ_API_KEY: str | None = Field(None, env="GROQ_API_KEY")
    # Hallucination prevention / rerank settings
    RAG_SIMILARITY_THRESHOLD: float = Field(0.35, env="RAG_SIMILARITY_THRESHOLD")
    RAG_RERANKER_MODEL: str | None = Field(None, env="RAG_RERANKER_MODEL")
    RAG_RERANK_ENABLED: bool = Field(True, env="RAG_RERANK_ENABLED")
    RAG_RERANK_TOP_K_FACTOR: int = Field(2, env="RAG_RERANK_TOP_K_FACTOR")
    RAG_VERIFICATION_MIN_OVERLAP: int = Field(2, env="RAG_VERIFICATION_MIN_OVERLAP")
    RAG_CONF_RETRIEVAL_WEIGHT: float = Field(0.6, env="RAG_CONF_RETRIEVAL_WEIGHT")
    RAG_CONF_VERIFICATION_WEIGHT: float = Field(0.4, env="RAG_CONF_VERIFICATION_WEIGHT")

    # pydantic-settings v2 config: allow extra env vars so unrelated keys don't cause failure
    model_config = {"extra": "ignore", "env_file": ".env", "env_file_encoding": "utf-8"}

    @validator("GROQ_API_KEY", pre=True, always=True)
    def validate_groq_api_key(cls, v):
        if not v:
            raise ValueError("GROQ_API_KEY must be set in environment for RAG generation")
        return v


settings = RAGSettings()

