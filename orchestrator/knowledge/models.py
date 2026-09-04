import uuid
import hashlib
import time
from typing import Any, Dict, List, Optional

class KnowledgeChunk:
    """
    Represents a single chunk of text from a knowledge base document.
    Extended in Phase 23 with scopes, versioning, content hashing, and user isolation.
    """
    def __init__(
        self,
        content: str,
        source: str,
        id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None,
        user_id: str = "global",
        scope: str = "global",               # global, user, project, temporary
        title: Optional[str] = None,
        chunk_index: int = 0,
        version: int = 1,
        content_hash: Optional[str] = None,
    ):
        if not content or not isinstance(content, str):
            raise ValueError("content must be a non-empty string.")
        if not source or not isinstance(source, str):
            raise ValueError("source must be a non-empty string.")

        self.id = id or str(uuid.uuid4())
        self.content = content.strip()
        self.source = source.strip()
        self.metadata = metadata or {}
        self.embedding = embedding
        self.user_id = user_id
        self.scope = scope
        self.title = title or source
        self.chunk_index = chunk_index
        self.version = version
        self.content_hash = content_hash or hashlib.sha256(self.content.encode("utf-8")).hexdigest()

        # Synchronize metadata dictionary
        self.metadata.update({
            "user_id": self.user_id,
            "scope": self.scope,
            "title": self.title,
            "chunk_index": self.chunk_index,
            "version": self.version,
            "content_hash": self.content_hash,
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "metadata": self.metadata,
            "embedding": self.embedding,
            "user_id": self.user_id,
            "scope": self.scope,
            "title": self.title,
            "chunk_index": self.chunk_index,
            "version": self.version,
            "content_hash": self.content_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeChunk":
        meta = data.get("metadata", {})
        return cls(
            id=data.get("id"),
            content=data["content"],
            source=data["source"],
            metadata=meta,
            embedding=data.get("embedding"),
            user_id=data.get("user_id") or meta.get("user_id", "global"),
            scope=data.get("scope") or meta.get("scope", "global"),
            title=data.get("title") or meta.get("title"),
            chunk_index=data.get("chunk_index") or meta.get("chunk_index", 0),
            version=data.get("version") or meta.get("version", 1),
            content_hash=data.get("content_hash") or meta.get("content_hash"),
        )
