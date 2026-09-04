import os
import json
import time
import logging
from typing import Any, Dict, Optional, Tuple

from orchestrator.cache.base import BaseCacheProvider
from orchestrator.observability import default_metrics, jarvis_logger

logger = logging.getLogger(__name__)

class MemoryFallbackCache:
    """
    In-memory fallback cache dictionary used when Redis is unavailable.
    """
    def __init__(self):
        self._store: Dict[str, Tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        val, expiry = self._store[key]
        if time.time() > expiry:
            del self._store[key]
            return None
        return val

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        expiry = time.time() + ttl_seconds
        self._store[key] = (value, expiry)
        return True

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def exists(self, key: str) -> bool:
        return self.get(key) is not None

    def flush(self) -> None:
        self._store.clear()

class HybridCacheProvider(BaseCacheProvider):
    """
    Hybrid cache provider attempting Redis first, falling back gracefully to in-memory caching if Redis is offline.
    Instrumented with cache hit/miss observability metrics.
    """
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._redis_client = None
        self._memory_cache = MemoryFallbackCache()
        self._is_redis_available = False

        self._init_redis()

    def _init_redis(self) -> None:
        try:
            import redis
            client = redis.Redis.from_url(self.redis_url, socket_timeout=1.0, decode_responses=True)
            client.ping()
            self._redis_client = client
            self._is_redis_available = True
            jarvis_logger.info("Connected to Redis cache successfully.")
        except Exception:
            self._is_redis_available = False
            jarvis_logger.info("Redis unavailable. Using in-memory fallback cache.")

    def get(self, key: str) -> Optional[Any]:
        if self._is_redis_available and self._redis_client:
            try:
                raw_val = self._redis_client.get(key)
                if raw_val is not None:
                    default_metrics.record_cache_hit()
                    return json.loads(raw_val)
                default_metrics.record_cache_miss()
                return None
            except Exception as exc:
                default_metrics.record_cache_error()
                jarvis_logger.warning("Redis get error: %s. Using memory fallback.", exc)
                self._is_redis_available = False

        val = self._memory_cache.get(key)
        if val is not None:
            default_metrics.record_cache_hit()
        else:
            default_metrics.record_cache_miss()
        return val

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        serialized = json.dumps(value)
        if self._is_redis_available and self._redis_client:
            try:
                self._redis_client.setex(key, ttl_seconds, serialized)
                return True
            except Exception as exc:
                default_metrics.record_cache_error()
                jarvis_logger.warning("Redis set error: %s. Using memory fallback.", exc)
                self._is_redis_available = False

        return self._memory_cache.set(key, value, ttl_seconds=ttl_seconds)

    def delete(self, key: str) -> bool:
        if self._is_redis_available and self._redis_client:
            try:
                self._redis_client.delete(key)
            except Exception:
                self._is_redis_available = False

        return self._memory_cache.delete(key)

    def exists(self, key: str) -> bool:
        if self._is_redis_available and self._redis_client:
            try:
                return bool(self._redis_client.exists(key))
            except Exception:
                self._is_redis_available = False

        return self._memory_cache.exists(key)

    def flush(self) -> None:
        if self._is_redis_available and self._redis_client:
            try:
                self._redis_client.flushdb()
            except Exception:
                pass
        self._memory_cache.flush()

default_cache = HybridCacheProvider()
