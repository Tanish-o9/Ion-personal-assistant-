import pytest
from orchestrator.memory.store import InMemoryStore, MemoryRecord
from orchestrator.memory.manager import MemoryManager
from orchestrator.memory import default_memory_manager, default_memory_store
from orchestrator.llm_client import LLMClient, LLMResponse
from orchestrator.graph import build_orchestrator_graph

class MockLLM(LLMClient):
    async def generate(self, messages, system_prompt=None, model_name="claude-3-5-sonnet-20241022"):
        return LLMResponse(
            text="I will format code in Python as per your preference.",
            model_used="mock-llm",
            token_count=12,
            latency_ms=5.0,
        )

# ---------------------------------------------------------------------------
# 1. Memory Store Unit Tests
# ---------------------------------------------------------------------------

def test_memory_store_save_and_retrieve():
    store = InMemoryStore()
    record = MemoryRecord(user_id="user_1", content="User prefers Python for backend", memory_type="preference")
    store.save(record)

    retrieved = store.get_by_user("user_1")
    assert len(retrieved) == 1
    assert retrieved[0].content == "User prefers Python for backend"
    assert retrieved[0].user_id == "user_1"

def test_memory_store_delete():
    store = InMemoryStore()
    record = MemoryRecord(user_id="user_1", content="User prefers FastAPI")
    store.save(record)

    deleted = store.delete(record.id, "user_1")
    assert deleted is True
    assert len(store.get_by_user("user_1")) == 0

# ---------------------------------------------------------------------------
# 2. Memory Manager Unit Tests & Bounded Limits
# ---------------------------------------------------------------------------

def test_memory_manager_bounded_retrieval():
    manager = MemoryManager(store=InMemoryStore(), default_limit=2)
    manager.save_memory("user_1", "Fact 1")
    manager.save_memory("user_1", "Fact 2")
    manager.save_memory("user_1", "Fact 3")

    mems = manager.get_memories("user_1")
    assert len(mems) == 2
    assert mems[0].content == "Fact 3"

# ---------------------------------------------------------------------------
# 3. User Isolation Tests (User A vs User B)
# ---------------------------------------------------------------------------

def test_user_memory_isolation():
    manager = MemoryManager(store=InMemoryStore())
    manager.save_memory("user_alice", "Alice prefers React")
    manager.save_memory("user_bob", "Bob prefers Django")

    alice_mems = manager.get_memories("user_alice")
    bob_mems = manager.get_memories("user_bob")

    assert len(alice_mems) == 1
    assert len(bob_mems) == 1

    assert alice_mems[0].content == "Alice prefers React"
    assert bob_mems[0].content == "Bob prefers Django"
    assert "Django" not in [m.content for m in alice_mems]

# ---------------------------------------------------------------------------
# 4. LangGraph Memory Loading & Context Injection Test
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_graph_memory_loading_and_injection():
    mock_llm = MockLLM()
    graph = build_orchestrator_graph(mock_llm)

    # 1. Pre-seed memory for user_dev
    default_memory_manager.save_memory("user_dev", "User prefers Python")

    config = {"configurable": {"thread_id": "session-mem-1"}}
    inputs = {
        "messages": [{"role": "user", "content": "Write a REST endpoint"}],
        "session_id": "session-mem-1",
        "user_id": "user_dev",
        "active_memory": [],
        "pending_action": None,
        "tool_round_count": 0,
    }

    final_state = await graph.ainvoke(inputs, config=config)
    active_memory = final_state.get("active_memory", [])

    assert len(active_memory) >= 1
    assert any("User prefers Python" in m.get("content", "") for m in active_memory)

# ---------------------------------------------------------------------------
# 5. Explicit Memory Capture Test
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_explicit_memory_extraction():
    mock_llm = MockLLM()
    graph = build_orchestrator_graph(mock_llm)
    user_id = "user_extractor_test"

    config = {"configurable": {"thread_id": "session-mem-2"}}
    inputs = {
        "messages": [{"role": "user", "content": "I prefer TypeScript for frontend code"}],
        "session_id": "session-mem-2",
        "user_id": user_id,
        "active_memory": [],
        "pending_action": None,
        "tool_round_count": 0,
    }

    await graph.ainvoke(inputs, config=config)

    user_mems = default_memory_manager.get_memories(user_id)
    assert len(user_mems) >= 1
    assert any("typescript" in m.content.lower() for m in user_mems)
