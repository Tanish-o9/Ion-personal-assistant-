import os
import json
import math
import logging
from typing import Any, Dict, List, Optional, Tuple

from orchestrator.knowledge.models import KnowledgeChunk
from orchestrator.knowledge.embeddings import BaseEmbeddingProvider, SimpleEmbeddingProvider

logger = logging.getLogger(__name__)

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Computes cosine similarity between two numeric vectors.
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0

    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

class LocalVectorStore:
    """
    Lightweight local vector store with file system JSON persistence and cosine similarity search.
    """
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.getenv("VECTOR_STORE_PATH", "knowledge_vector_store.json")
        self._chunks: Dict[str, KnowledgeChunk] = {}
        if os.path.exists(self.storage_path):
            self.load()

    def add_chunks(self, chunks: List[KnowledgeChunk], embedding_provider: Optional[BaseEmbeddingProvider] = None) -> None:
        """
        Embeds missing chunks and adds them to the vector store.
        """
        provider = embedding_provider or SimpleEmbeddingProvider()
        for chunk in chunks:
            if chunk.embedding is None:
                chunk.embedding = provider.embed(chunk.content)
            self._chunks[chunk.id] = chunk

        self.save()

    def add(self, chunks: List[KnowledgeChunk], embedding_provider: Optional[BaseEmbeddingProvider] = None) -> None:
        """
        Alias for add_chunks.
        """
        self.add_chunks(chunks, embedding_provider)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> List[Tuple[KnowledgeChunk, float]]:
        """
        Performs cosine similarity search against query_embedding.
        Returns top_k (KnowledgeChunk, score) tuples filtered by min_score.
        """
        if not self._chunks or not query_embedding:
            return []

        results: List[Tuple[KnowledgeChunk, float]] = []
        for chunk in self._chunks.values():
            if chunk.embedding is None:
                continue
            sim = cosine_similarity(query_embedding, chunk.embedding)
            if sim >= min_score:
                results.append((chunk, sim))

        results.sort(key=lambda item: item[1], reverse=True)
        return results[:top_k]

    def delete(self, chunk_id: str) -> bool:
        """
        Deletes a KnowledgeChunk by ID.
        """
        if chunk_id in self._chunks:
            del self._chunks[chunk_id]
            self.save()
            return True
        return False

    def clear(self) -> None:
        """
        Clears all stored chunks.
        """
        self._chunks.clear()
        self.save()

    def save(self, path: Optional[str] = None) -> None:
        """
        Persists vector store data to local JSON file.
        """
        target_path = path or self.storage_path
        data = [chunk.to_dict() for chunk in self._chunks.values()]
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as exc:
            logger.warning("Failed to save vector store to '%s': %s", target_path, exc)

    def load(self, path: Optional[str] = None) -> None:
        """
        Loads vector store data from local JSON file.
        """
        target_path = path or self.storage_path
        if not os.path.exists(target_path):
            return

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._chunks = {item["id"]: KnowledgeChunk.from_dict(item) for item in data}
        except Exception as exc:
            logger.warning("Failed to load vector store from '%s': %s", target_path, exc)
