import pytest
from fastapi.testclient import TestClient

from orchestrator.memory import (
    MemoryRecord,
    InMemoryStore,
    MemoryManager,
    format_memories_for_context,
    score_memory_relevance,
    VALID_MEMORY_TYPES,
)
from orchestrator.llm_client import LLMClient, LLMResponse
from orchestrator.graph import build_orchestrator_graph
from api.main import app

class MockLLM(LLMClient):
    async def generate(self, messages, system_prompt=None, model_name="claude-3-5-sonnet-20241022"):
        return LLMResponse(
            text="Here is a clean Python project structure for JARVIS.",
            model_used="mock-llm",
            token_count=15,
            latency_ms=5.0,
        )

# ---------------------------------------------------------------------------
# 1. Memory Types & Importance Validation Tests
# ---------------------------------------------------------------------------

def test_memory_types_and_importance_clamping():
    r1 = MemoryRecord(user_id="u1", content="Prefers Python", memory_type="preference", importance=5)
    r2 = MemoryRecord(user_id="u1", content="Building JARVIS", memory_type="project", importance=4)
    r3 = MemoryRecord(user_id="u1", content="Student profile", memory_type="profile", importance=2)
    r4 = MemoryRecord(user_id="u1", content="Detailed steps", memory_type="instruction", importance=1)

    assert r1.memory_type == "preference"
    assert r1.importance == 5
    assert r2.memory_type == "project"
    assert r3.memory_type == "profile"
    assert r4.memory_type == "instruction"

    # Test invalid memory_type fallback and importance clamping
    r_invalid = MemoryRecord(user_id="u1", content="Test invalid", memory_type="random_type", importance=10)
    assert r_invalid.memory_type == "preference"
    assert r_invalid.importance == 5

# ---------------------------------------------------------------------------
# 2. Relevance Scoring & Importance Ranking Tests
# ---------------------------------------------------------------------------

def test_memory_scoring_relevance_and_importance():
    r_low_imp = MemoryRecord(user_id="u1", content="Random note", importance=1)
    r_high_imp = MemoryRecord(user_id="u1", content="Random note", importance=5)

    s1 = score_memory_relevance(r_low_imp, query="something", index=0, total_count=2)
    s2 = score_memory_relevance(r_high_imp, query="something", index=0, total_count=2)
    assert s2 > s1

def test_keyword_relevance_scoring():
    r_python = MemoryRecord(user_id="u1", content="User prefers Python programming examples", importance=3)
    r_event = MemoryRecord(user_id="u1", content="User is organizing a college event", importance=3)

    query = "Show me a Python API example"
    score_py = score_memory_relevance(r_python, query=query, index=0, total_count=2)
    score_ev = score_memory_relevance(r_event, query=query, index=0, total_count=2)

    assert score_py > score_ev

def test_memory_ranking_and_bounded_limit():
    manager = MemoryManager(store=InMemoryStore(), max_active_memories=5)
    user_id = "user_rank_test"

    # Save 10 memories with varying importance
    for i in range(1, 11):
        manager.save_memory(user_id, f"Memory item {i}", memory_type="preference", importance=i % 5 + 1)

    # Add a highly relevant memory
    manager.save_memory(user_id, "User prefers FastAPI framework", memory_type="preference", importance=5)

    top_memories = manager.get_relevant_memories(user_id, query="FastAPI framework", limit=5)
    assert len(top_memories) == 5
    assert top_memories[0].content == "User prefers FastAPI framework"

# ---------------------------------------------------------------------------
# 3. Context Formatter Tests
# ---------------------------------------------------------------------------

def test_format_memories_for_context():
    m1 = MemoryRecord(user_id="u1", content="User prefers Python examples", memory_type="preference")
    m2 = MemoryRecord(user_id="u1", content="User is building JARVIS AT SCALE", memory_type="project")

    formatted = format_memories_for_context([m1, m2])
    assert "Relevant user memories:" in formatted
    assert "- [PREFERENCE] User prefers Python examples" in formatted
    assert "- [PROJECT] User is building JARVIS AT SCALE" in formatted

# ---------------------------------------------------------------------------
# 4. Memory Conflict & Preference Override Tests
# ---------------------------------------------------------------------------

def test_preference_update_conflict_override():
    manager = MemoryManager(store=InMemoryStore())
    user_id = "user_override"

    manager.save_memory(user_id, "User prefers Java", memory_type="preference")
    manager.save_memory(user_id, "User prefers Python", memory_type="preference")

    memories = manager.get_relevant_memories(user_id)
    assert len(memories) == 1
    assert "Python" in memories[0].content

# ---------------------------------------------------------------------------
# 5. Multi-Turn REST API End-to-End Test (POST /chat)
# ---------------------------------------------------------------------------

def test_api_chat_multi_turn_memory_flow():
    client = TestClient(app)
    reg_res = client.post("/auth/register", json={"username": "mem_turn_user", "password": "memturnpassword"}).json()
    token = reg_res["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Turn 1: Save project preference
    res1 = client.post(
        "/chat",
        json={"text": "I am building a Python project called JARVIS"},
        headers=headers,
    )
    assert res1.status_code == 200

    # Turn 2: Query project folder structure
    res2 = client.post(
        "/chat",
        json={"text": "Give me a good folder structure for it"},
        headers=headers,
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert "session_id" in data2
    assert len(data2["response"]) > 0
