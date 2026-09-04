import pytest
from fastapi.testclient import TestClient

from orchestrator.tools import (
    ToolExecutor,
    ToolResult,
    ToolRegistry,
    CalculatorTool,
    default_registry,
    default_executor,
)
from orchestrator.llm_client import LLMClient, LLMResponse
from orchestrator.graph import build_orchestrator_graph
from api.main import app

class MockLLM(LLMClient):
    async def generate(self, messages, system_prompt=None, model_name="claude-3-5-sonnet-20241022"):
        last_msg = messages[-1]["content"] if messages else ""
        return LLMResponse(
            text=f"LLM Response to '{last_msg}'",
            model_used="mock-llm",
            token_count=10,
            latency_ms=5.0,
        )

# ---------------------------------------------------------------------------
# 1. Tool Executor Unit Tests
# ---------------------------------------------------------------------------

def test_executor_valid_tool():
    executor = ToolExecutor(default_registry)
    res = executor.execute("calculator", operation="add", a=20, b=30)
    assert res.success is True
    assert res.output == 50
    assert res.error is None
    assert res.to_dict()["tool_name"] == "calculator"

def test_executor_unknown_tool():
    executor = ToolExecutor(default_registry)
    res = executor.execute("nonexistent_tool", arg=123)
    assert res.success is False
    assert res.output is None
    assert "Unknown tool" in res.error

def test_executor_tool_error_handling():
    executor = ToolExecutor(default_registry)
    res = executor.execute("calculator", operation="divide", a=10, b=0)
    assert res.success is False
    assert res.output is None
    assert "Division by zero" in res.error

# ---------------------------------------------------------------------------
# 2. Graph Agent -> Tool Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_graph_agent_tool_execution_flow():
    mock_llm = MockLLM()
    graph = build_orchestrator_graph(mock_llm)

    test_cases = [
        ("What is 25 + 75?", "100"),
        ("Calculate 12 * 8", "96"),
        ("What is 100 / 4?", "25"),
    ]

    for user_prompt, expected_val in test_cases:
        config = {"configurable": {"thread_id": f"test-tool-{expected_val}"}}
        inputs = {
            "messages": [{"role": "user", "content": user_prompt}],
            "session_id": f"test-tool-{expected_val}",
            "user_id": "test_user",
            "active_memory": [],
            "pending_action": None,
            "tool_round_count": 0,
        }

        final_state = await graph.ainvoke(inputs, config=config)
        messages = final_state.get("messages", [])
        assert len(messages) > 0

        last_content = messages[-1].content if hasattr(messages[-1], "content") else messages[-1]["content"]
        assert expected_val in last_content

@pytest.mark.asyncio
async def test_graph_agent_tool_error_resilience():
    mock_llm = MockLLM()
    graph = build_orchestrator_graph(mock_llm)
    config = {"configurable": {"thread_id": "test-div-zero"}}

    inputs = {
        "messages": [{"role": "user", "content": "What is 10 / 0?"}],
        "session_id": "test-div-zero",
        "user_id": "test_user",
        "active_memory": [],
        "pending_action": None,
        "tool_round_count": 0,
    }

    final_state = await graph.ainvoke(inputs, config=config)
    messages = final_state.get("messages", [])
    last_content = messages[-1].content if hasattr(messages[-1], "content") else messages[-1]["content"]
    assert "Calculation error" in last_content or "Division by zero" in last_content

# ---------------------------------------------------------------------------
# 3. REST API Endpoint Integration Test
# ---------------------------------------------------------------------------

def test_api_chat_calculator_integration():
    client = TestClient(app)
    reg_res = client.post("/auth/register", json={"username": "calc_user", "password": "calcpassword"}).json()
    token = reg_res["token"]

    response = client.post(
        "/chat",
        json={"text": "What is 25 * 8?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "200" in data["response"]
