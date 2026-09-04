import os
import math
import re
import hashlib
from abc import ABC, abstractmethod
from typing import List, Optional
from orchestrator.cache import default_cache, make_cache_key

class BaseEmbeddingProvider(ABC):
    """
    Abstract interface for text embedding providers.
    """
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        pass

class SimpleEmbeddingProvider(BaseEmbeddingProvider):
    """
    Lightweight, deterministic local feature-hashing embedding provider.
    Generates unit-normalized 64-dimensional dense vectors with 24-hour result caching.
    """
    def __init__(self, vector_dim: int = 64, api_key: Optional[str] = None):
        self.vector_dim = vector_dim
        self.api_key = api_key or os.getenv("EMBEDDING_API_KEY")

    def _normalize(self, vec: List[float]) -> List[float]:
        norm = math.sqrt(sum(x * x for x in vec))
        if norm == 0:
            return [0.0] * self.vector_dim
        return [x / norm for x in vec]

    def embed(self, text: str) -> List[float]:
        if not text or not text.strip():
            return [0.0] * self.vector_dim

        clean_text = text.strip()
        cache_key = make_cache_key("embedding", f"dim{self.vector_dim}", clean_text)

        cached_vec = default_cache.get(cache_key)
        if cached_vec is not None:
            return cached_vec

        vec = [0.0] * self.vector_dim
        words = re.findall(r"\w+", clean_text.lower())

        for word in words:
            hash_val = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = hash_val % self.vector_dim
            sign = 1.0 if (hash_val // self.vector_dim) % 2 == 0 else -1.0
            vec[idx] += sign

        normalized_vec = self._normalize(vec)
        default_cache.set(cache_key, normalized_vec, ttl_seconds=86400)
        return normalized_vec

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(t) for t in texts]
