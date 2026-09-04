import time
import hashlib
from abc import ABC, abstractmethod
from typing import Any, Optional

class BaseCacheProvider(ABC):
    """
    Abstract cache provider interface supporting set, get, delete, exists, and flush operations.
    """
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    def flush(self) -> None:
        pass

def make_cache_key(namespace: str, *parts: str) -> str:
    """
    Generates a deterministic, hashed cache key formatted as namespace:hash.
    """
    combined = ":".join(str(p) for p in parts)
    content_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()[:16]
    return f"{namespace}:{content_hash}"
