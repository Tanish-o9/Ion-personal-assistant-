import os
import json
import uuid
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional

from database.repository import MemoryRepository

logger = logging.getLogger(__name__)

VALID_MEMORY_TYPES = {
    "preference", "project", "profile", "instruction",
    "fact", "relationship", "task_context", "learned_behavior"
}

class MemoryRecord:
    """
    Represents a single user memory unit.
    """
    def __init__(
        self,
        user_id: str,
        content: str,
        memory_type: str = "preference",
        importance: int = 3,
        id: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        if not user_id or not isinstance(user_id, str):
            raise ValueError("user_id must be a non-empty string.")
        if not content or not isinstance(content, str):
            raise ValueError("content must be a non-empty string.")

        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.content = content.strip()

        clean_type = memory_type.lower().strip() if memory_type else "preference"
        self.memory_type = clean_type if clean_type in VALID_MEMORY_TYPES else "preference"

        try:
            imp_val = int(importance)
            self.importance = max(1, min(5, imp_val))
        except (ValueError, TypeError):
            self.importance = 3

        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "memory_type": self.memory_type,
            "importance": self.importance,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "MemoryRecord":
        return cls(
            id=data.get("id"),
            user_id=data["user_id"],
            content=data["content"],
            memory_type=data.get("memory_type", "preference"),
            importance=data.get("importance", 3),
            created_at=data.get("created_at"),
        )

class BaseMemoryStore(ABC):
    @abstractmethod
    def save(self, record: MemoryRecord) -> None:
        pass

    @abstractmethod
    def get_by_user(self, user_id: str) -> List[MemoryRecord]:
        pass

    @abstractmethod
    def delete(self, memory_id: str, user_id: str) -> bool:
        pass

class InMemoryStore(BaseMemoryStore):
    """
    Database-backed memory store with user isolation.
    """
    def save(self, record: MemoryRecord) -> None:
        db_mem = MemoryRepository.save_memory(
            user_id=record.user_id,
            content=record.content,
            memory_type=record.memory_type,
            importance=record.importance,
            id=record.id,
        )
        record.id = db_mem.id

    def get_by_user(self, user_id: str) -> List[MemoryRecord]:
        if not user_id:
            return []
        db_mems = MemoryRepository.get_user_memories(user_id=user_id, limit=50)
        return [
            MemoryRecord(
                id=m.id,
                user_id=m.user_id,
                content=m.content,
                memory_type=m.memory_type,
                importance=m.importance,
                created_at=m.created_at,
            )
            for m in db_mems
        ]

    def delete(self, memory_id: str, user_id: str) -> bool:
        return MemoryRepository.delete_memory(memory_id, user_id)

default_memory_store = InMemoryStore()
