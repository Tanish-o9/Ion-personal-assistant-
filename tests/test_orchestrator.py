import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from orchestrator.llm_client import LLMClient, LLMResponse
from orchestrator.graph import build_orchestrator_graph
from api.main import app, graph_app

class MockLLMClient(LLMClient):
    def __init__(self, simulate_failure: bool = False):
        super().__init__()
        self.simulate_failure = simulate_failure

    async def generate(self, messages, system_prompt=None, model_name="claude-3-5-sonnet-20241022"):
        if self.simulate_failure:
            return LLMResponse(
                text="I am operating in fallback mode. How can I assist you today?",
                model_used="local_fallback",
                token_count=0,
                latency_ms=10.0
            )

        last_msg = messages[-1]["content"] if messages else ""
        return LLMResponse(
            text=f"Mocked response to: '{last_msg}'",
            model_used="mock-claude-3-5",
            token_count=42,
            latency_ms=15.0
        )

@pytest.mark.asyncio
async def test_intent_classification_and_routing():
    mock_llm = MockLLMClient()
    test_graph = build_orchestrator_graph(mock_llm)

    utterances = [
        ("Hello, how are you?", "chat"),
        ("Write a Python function to sort a list", "coding_task"),
        ("Research quantum computing breakthroughs", "research_task"),
        ("Open Spotify app and increase volume", "system_task"),
        ("Schedule a team sync tomorrow at 3pm", "scheduling_task"),
    ]

    for utterance, expected_intent in utterances:
        config = {"configurable": {"thread_id": f"test-intent-{expected_intent}"}}
        inputs = {
            "messages": [{"role": "user", "content": utterance}],
            "session_id": f"test-intent-{expected_intent}",
            "user_id": "test_user",
            "active_memory": [],
            "pending_action": None,
        }
        res = await test_graph.ainvoke(inputs, config=config)
        assert res["intent"] == expected_intent
        assert "messages" in res
        assert len(res["messages"]) > 0

@pytest.mark.asyncio
async def test_graph_session_checkpoint_persistence():
    mock_llm = MockLLMClient()
    test_graph = build_orchestrator_graph(mock_llm)
    session_id = "persistent-session-123"
    config = {"configurable": {"thread_id": session_id}}

    inputs_turn1 = {
        "messages": [{"role": "user", "content": "My name is Tanish"}],
        "session_id": session_id,
        "user_id": "test_user",
        "active_memory": [],
        "pending_action": None,
    }
    await test_graph.ainvoke(inputs_turn1, config=config)

    # State retrieval simulation
    checkpoint_state = await test_graph.aget_state(config=config)
    messages = checkpoint_state.values.get("messages", [])
    assert len(messages) >= 2  # user message + assistant response

    # Turn 2 using same session_id resumes context
    inputs_turn2 = {
        "messages": [{"role": "user", "content": "What is my name?"}],
        "session_id": session_id,
        "user_id": "test_user",
        "active_memory": [],
        "pending_action": None,
    }
    await test_graph.ainvoke(inputs_turn2, config=config)
    state2 = await test_graph.aget_state(config=config)
    assert len(state2.values["messages"]) >= 4

def test_api_chat_endpoint():
    client = TestClient(app)
    reg_res = client.post("/auth/register", json={"username": "orch_user", "password": "orchpassword"}).json()
    token = reg_res["token"]

    response = client.post(
        "/chat",
        json={"text": "Write a Python script to filter logs"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "response" in data
    assert data["intent"] == "coding_task"

@pytest.mark.asyncio
async def test_llm_fallback():
    failing_llm = MockLLMClient(simulate_failure=True)
    res = await failing_llm.generate([{"role": "user", "content": "test"}])
    assert res.model_used == "local_fallback"
    assert "fallback mode" in res.text
