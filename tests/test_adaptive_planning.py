import pytest
from typing import Dict, Any

from orchestrator.planning import (
    TaskPlan,
    TaskStep,
    ComplexityAssessor,
    IntelligentToolSelector,
    Planner,
    TaskExecutor,
    AdaptiveVerifier,
    classify_failure,
)
from orchestrator.tools import default_registry, ToolExecutor
from orchestrator.tools.interface import BaseTool

class MockFailingTool(BaseTool):
    def __init__(self, name: str = "failing_tool", fail_count: int = 1):
        super().__init__(
            name=name,
            description="A tool that fails initially then succeeds.",
            capabilities=["testing"],
            risk_level="low",
        )
        self.fail_count = fail_count
        self.attempts = 0

    def execute(self, *args, **kwargs):
        self.attempts += 1
        if self.attempts <= self.fail_count:
            raise ConnectionError("Network connection timeout.")
        return "Recovered success output"

# ---------------------------------------------------------------------------
# 1. Complexity Assessment & Route Selection Tests
# ---------------------------------------------------------------------------

def test_complexity_assessor_route_selection():
    # 1. Direct response
    assert ComplexityAssessor.assess_route("Hello Jarvis") == "direct_response"

    # 2. Single tool math query
    assert ComplexityAssessor.assess_route("What is 15 * 4?") == "single_tool"

    # 3. Knowledge task RAG query
    assert ComplexityAssessor.assess_route("Search internal doc for project status") == "knowledge_task"

    # 4. Web research task
    assert ComplexityAssessor.assess_route("Search the web for Python 3.13 features") == "research_task"

    # 5. Multi-step task
    assert ComplexityAssessor.assess_route("Calculate 20 + 30 and then explain the result") == "multi_step_task"

    # 6. Background task
    assert ComplexityAssessor.assess_route("Deep research", is_background=True) == "background_task"

    # 7. Multimodal task
    assert ComplexityAssessor.assess_route("Analyze image", has_files=True) == "multimodal_task"

# ---------------------------------------------------------------------------
# 2. Failure Classification & Retry Tests
# ---------------------------------------------------------------------------

def test_failure_classification_categories():
    assert classify_failure("Connection timeout error") == "timeout"
    assert classify_failure("HTTP 500 Network failure") == "external_service_failure"
    assert classify_failure("Unknown tool 'foo' is not registered") == "tool_unavailable"
    assert classify_failure("ValueError: invalid argument") == "invalid_input"
    assert classify_failure("Access denied for user") == "authorization_failure"

# ---------------------------------------------------------------------------
# 3. Intelligent Tool Selection & Validation Tests
# ---------------------------------------------------------------------------

def test_intelligent_tool_selection_and_backend_validation():
    selector = IntelligentToolSelector(registry=default_registry)

    # Capability matching
    calc_tool = selector.select_tool_for_step("Perform arithmetic calculation", required_capability="math")
    assert calc_tool is not None
    assert calc_tool.name == "calculator"

    # Validation check for registered vs unregistered tools
    is_valid, err = selector.validate_tool_execution("calculator", {}, user_id="user_1")
    assert is_valid is True
    assert err is None

    is_valid_unknown, err_unknown = selector.validate_tool_execution("non_existent_tool", {}, user_id="user_1")
    assert is_valid_unknown is False
    assert "Unknown tool" in err_unknown

# ---------------------------------------------------------------------------
# 4. Adaptive Execution, Bounded Retries & Self-Correction Tests
# ---------------------------------------------------------------------------

def test_task_executor_retry_and_recovery():
    tool = MockFailingTool(fail_count=1)
    reg = default_registry
    reg.register(tool)
    t_executor = ToolExecutor(reg)
    executor = TaskExecutor(tool_executor=t_executor)

    plan = TaskPlan(task_description="Test retry recovery", route="multi_step_task")
    step = TaskStep(step_id=1, description="Execute failing tool", tool_name="failing_tool")
    plan.add_step(step)

    executed_plan = executor.execute_plan(plan)
    assert executed_plan.status == "completed"
    assert executed_plan.steps[0].status == "completed"
    assert executed_plan.steps[0].result == "Recovered success output"
    assert executed_plan.steps[0].retry_count == 1

# ---------------------------------------------------------------------------
# 5. Adaptive Verifier & Confidence Scoring Tests
# ---------------------------------------------------------------------------

def test_adaptive_verifier_confidence_scoring():
    # 1. High confidence plan (no retries, no replans)
    plan_high = TaskPlan(task_description="High confidence task")
    plan_high.add_step(TaskStep(step_id=1, description="Step 1", status="completed"))
    res_high = AdaptiveVerifier.verify_plan(plan_high)
    assert res_high["verified"] is True
    assert res_high["confidence"] == "high"

    # 2. Medium confidence plan (with replans or retries)
    plan_med = TaskPlan(task_description="Medium confidence task", replan_count=1)
    plan_med.add_step(TaskStep(step_id=1, description="Step 1", status="completed"))
    res_med = AdaptiveVerifier.verify_plan(plan_med)
    assert res_med["verified"] is True
    assert res_med["confidence"] == "medium"
