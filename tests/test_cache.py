import time
import pytest
from fastapi.testclient import TestClient

from api.main import app
from orchestrator.cache import (
    HybridCacheProvider,
    MemoryFallbackCache,
    default_cache,
    make_cache_key,
)
from orchestrator.tools.web import WebSearchTool, BaseSearchProvider
from orchestrator.knowledge.embeddings import SimpleEmbeddingProvider
from orchestrator.knowledge.retriever import KnowledgeRetriever
from orchestrator.knowledge.vector_store import LocalVectorStore
from orchestrator.knowledge.models import KnowledgeChunk
from orchestrator.memory import default_memory_manager

class MockCountSearchProvider(BaseSearchProvider):
    def __init__(self):
        self.call_count = 0

    def search(self, query: str):
        self.call_count += 1
        return [
            {
                "title": f"Result {self.call_count} for {query}",
                "url": f"https://example.com/{query}",
                "snippet": f"Content {self.call_count}",
            }
        ]

# ---------------------------------------------------------------------------
# 1. Base & Hybrid Cache Provider Unit Tests
# ---------------------------------------------------------------------------

def test_cache_provider_get_set_delete_and_expiration():
    cache = HybridCacheProvider()
    cache.flush()

    assert cache.get("non_existent") is None
    assert cache.exists("non_existent") is False

    # Set value with short 1-second TTL
    assert cache.set("test_key", {"foo": "bar"}, ttl_seconds=1) is True
    assert cache.exists("test_key") is True
    assert cache.get("test_key") == {"foo": "bar"}

    # Delete value
    cache.delete("test_key")
    assert cache.get("test_key") is None

    # TTL Expiration test
    cache.set("expire_key", "temporary", ttl_seconds=1)
    time.sleep(1.1)
    assert cache.get("expire_key") is None

def test_make_cache_key_deterministic():
    key1 = make_cache_key("web_search", "python django")
    key2 = make_cache_key("web_search", "python django")
    key3 = make_cache_key("web_search", "python fastapi")

    assert key1 == key2
    assert key1 != key3
    assert key1.startswith("web_search:")

# ---------------------------------------------------------------------------
# 2. Web Search Caching Integration Test
# ---------------------------------------------------------------------------

def test_web_search_caching_and_hit_reuse():
    default_cache.flush()
    provider = MockCountSearchProvider()
    tool = WebSearchTool(provider=provider, ttl_seconds=300)

    # 1st call: Cache miss, invokes provider search (call_count = 1)
    res1 = tool.execute(query="FastAPI Caching")
    assert len(res1) == 1
    assert res1[0]["title"] == "Result 1 for FastAPI Caching"
    assert provider.call_count == 1

    # 2nd call: Cache hit, reuses cached result without invoking provider search (call_count stays 1)
    res2 = tool.execute(query="FastAPI Caching")
    assert len(res2) == 1
    assert res2[0]["title"] == "Result 1 for FastAPI Caching"
    assert provider.call_count == 1

# ---------------------------------------------------------------------------
# 3. Embedding Caching Integration Test
# ---------------------------------------------------------------------------

def test_embedding_caching_reuse():
    default_cache.flush()
    embedder = SimpleEmbeddingProvider(vector_dim=64)

    text = "Artificial intelligence and agentic workflows."
    key = make_cache_key("embedding", "dim64", text.strip())

    assert default_cache.get(key) is None

    # 1st call: Computes vector and caches it
    vec1 = embedder.embed(text)
    assert len(vec1) == 64
    assert default_cache.get(key) is not None

    # 2nd call: Hits cache
    vec2 = embedder.embed(text)
    assert vec1 == vec2

# ---------------------------------------------------------------------------
# 4. RAG Retrieval Caching Integration Test
# ---------------------------------------------------------------------------

def test_rag_retrieval_caching():
    default_cache.flush()
    store = LocalVectorStore()
    chunk = KnowledgeChunk(id="c1", content="Python is a programming language.", source="python.md")
    embedder = SimpleEmbeddingProvider()
    chunk.embedding = embedder.embed(chunk.content)
    store.add_chunks([chunk])

    retriever = KnowledgeRetriever(vector_store=store, embedding_provider=embedder)

    # 1st retrieval: Cache miss, performs vector search
    res1 = retriever.retrieve("Python language")
    assert len(res1) >= 1

    # 2nd retrieval: Hits cache and returns reconstructed objects
    res2 = retriever.retrieve("Python language")
    assert len(res2) == len(res1)
    assert res2[0][0].content == res1[0][0].content

# ---------------------------------------------------------------------------
# 5. User Profile Caching & Invalidation API Test
# ---------------------------------------------------------------------------

def test_user_profile_caching_and_invalidation():
    client = TestClient(app)
    default_cache.flush()

    # Register user
    reg = client.post("/auth/register", json={"username": "cache_user", "password": "cachepassword"}).json()
    token = reg["token"]
    user_id = reg["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}

    # Save a memory record for user
    mem_rec = default_memory_manager.save_memory(user_id=user_id, content="User prefers Python", memory_type="preference")

    # 1st profile call: Cache miss, computes profile and caches
    res1 = client.get(f"/profile/{user_id}", headers=headers).json()
    assert res1["username"] == "Cache_user"
    assert default_cache.get(f"profile:{user_id}") is not None

    # 2nd profile call: Hits profile cache
    res2 = client.get(f"/profile/{user_id}", headers=headers).json()
    assert res2["username"] == "Cache_user"

    # Deleting the valid memory record invalidates profile cache
    res_del = client.delete(f"/memory/{user_id}/{mem_rec.id}", headers=headers)
    assert res_del.status_code == 200
    assert default_cache.get(f"profile:{user_id}") is None
