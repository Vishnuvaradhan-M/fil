from __future__ import annotations
from typing import List, Iterable
import threading
import logging
import torch
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("app.rag.embeddings")


class EmbeddingModel:
    _instance: "EmbeddingModel" | None = None
    _lock = threading.Lock()

    def __init__(self, model_name: str):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info("Loading embedding model %s on %s", model_name, device)
        self.model = SentenceTransformer(model_name, device=device)

    @classmethod
    def get_instance(cls, model_name: str) -> "EmbeddingModel":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = EmbeddingModel(model_name)
        return cls._instance

    def embed_documents(self, texts: Iterable[str], batch_size: int = 32) -> List[List[float]]:
        texts_list = list(texts)
        embeddings = self.model.encode(texts_list, batch_size=batch_size, show_progress_bar=False, convert_to_numpy=True)
        return [e.tolist() for e in embeddings]

    def embed_query(self, query: str) -> List[float]:
        emb = self.model.encode([query], show_progress_bar=False, convert_to_numpy=True)[0]
        return emb.tolist()

