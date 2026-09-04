import pytest
from fastapi.testclient import TestClient

from orchestrator.planning.models import TaskStep, TaskPlan, MAX_PLAN_STEPS
from orchestrator.planning.planner import Planner
from orchestrator.planning.executor import TaskExecutor, Verifier
from orchestrator.tools import ToolExecutor, default_registry
from orchestrator.llm_client import LLMClient, LLMResponse
from orchestrator.graph import build_orchestrator_graph
from api.main import app

class MockLLM(LLMClient):
    async def generate(self, messages, system_prompt=None, model_name="claude-3-5-sonnet-20241022"):
        return LLMResponse(
            text="General response from mock LLM.",
            model_used="mock-llm",
            token_count=10,
            latency_ms=5.0,
        )

# ---------------------------------------------------------------------------
# 1. Task Step & Plan Model Tests
# ---------------------------------------------------------------------------

def test_task_step_and_plan_models():
    step1 = TaskStep(step_id=1, description="Step 1 description", tool_name="calculator", arguments={"operation": "add", "a": 5, "b": 5})
    assert step1.step_id == 1
    assert step1.status == "pending"

    plan = TaskPlan(task_description="Test multi-step task", steps=[step1])
    assert len(plan.steps) == 1
    assert plan.status == "pending"

    # Enforce max steps
    for i in range(2, 10):
        plan.add_step(TaskStep(step_id=i, description=f"Step {i}"))
    assert len(plan.steps) == MAX_PLAN_STEPS

# ---------------------------------------------------------------------------
# 2. Planner Fast Path vs Multi-step Tests
# ---------------------------------------------------------------------------

def test_planner_fast_path_bypass():
    planner = Planner()
    assert planner.requires_planning("Hello") is False
    assert planner.requires_planning("What is 10 + 20?") is False

def test_planner_multi_step_creation():
    planner = Planner()
    query = "Calculate 20 * 5 and then explain whether the answer is greater than 50"
    assert planner.requires_planning(query) is True

    plan = planner.create_plan(query)
    assert len(plan.steps) >= 2
    assert plan.steps[0].tool_name == "calculator"
    assert plan.steps[0].arguments["operation"] == "multiply"

# ---------------------------------------------------------------------------
# 3. Task Executor & Verifier Tests
# ---------------------------------------------------------------------------

def test_task_executor_success_flow():
    executor = TaskExecutor(tool_executor=ToolExecutor(default_registry))
    plan = TaskPlan(task_description="Test calculation plan")
    step1 = TaskStep(step_id=1, description="Calculate 20 * 5", tool_name="calculator", arguments={"operation": "multiply", "a": 20, "b": 5})
    step2 = TaskStep(step_id=2, description="Compare with 50", tool_name=None, arguments={"compare_to": 50})
    plan.add_step(step1)
    plan.add_step(step2)

    executed_plan = executor.execute_plan(plan)
    assert executed_plan.status == "completed"
    assert executed_plan.steps[0].status == "completed"
    assert executed_plan.steps[0].result == 100
    assert executed_plan.steps[1].status == "completed"
    assert "greater than 50" in str(executed_plan.steps[1].result)

    verification = Verifier.verify(executed_plan)
    assert verification["verified"] is True
    assert verification["completed_steps"] == 2

def test_task_executor_failure_stops_execution():
    executor = TaskExecutor(tool_executor=ToolExecutor(default_registry))
    plan = TaskPlan(task_description="Test failing plan")
    step1 = TaskStep(step_id=1, description="Divide by zero", tool_name="calculator", arguments={"operation": "divide", "a": 10, "b": 0})
    step2 = TaskStep(step_id=2, description="Dependent step", tool_name=None)
    plan.add_step(step1)
    plan.add_step(step2)

    executed_plan = executor.execute_plan(plan)
    assert executed_plan.status == "failed"
    assert executed_plan.steps[0].status == "failed"
    assert executed_plan.steps[1].status == "pending"  # Dependent step not run

# ---------------------------------------------------------------------------
# 4. Graph & REST API Integration Tests (POST /chat)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_graph_planning_flow():
    mock_llm = MockLLM()
    graph = build_orchestrator_graph(mock_llm)
    config = {"configurable": {"thread_id": "session-plan-1"}}

    inputs = {
        "messages": [{"role": "user", "content": "Calculate 20 * 5 and explain whether the result is greater than 50"}],
        "session_id": "session-plan-1",
        "user_id": "test_planner_user",
        "active_memory": [],
        "pending_action": None,
        "tool_round_count": 0,
    }

    final_state = await graph.ainvoke(inputs, config=config)
    assert "current_plan" in final_state
    assert final_state["current_plan"] is not None
    messages = final_state.get("messages", [])
    last_content = messages[-1].content if hasattr(messages[-1], "content") else messages[-1]["content"]
    assert "100" in last_content

def test_api_chat_multi_step_planning():
    client = TestClient(app)
    reg_res = client.post("/auth/register", json={"username": "plan_user", "password": "planpassword"}).json()
    token = reg_res["token"]

    res = client.post(
        "/chat",
        json={"text": "Calculate 20 * 5 and then explain whether the answer is greater than 50"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    assert "100" in data["response"]
