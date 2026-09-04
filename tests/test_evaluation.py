import pytest
from orchestrator.evaluation import (
    EvaluationPlatform,
    EvaluationCase,
    default_evaluation_platform,
)

def test_deterministic_evaluation_case():
    eval_plat = EvaluationPlatform()
    case = EvaluationCase(
        case_id="c1",
        category="tool_use",
        input_prompt="Calculate 15 + 25",
        expected_tool="calculator",
        expected_keywords=["40"],
    )

    res_pass = eval_plat.evaluate_case(case, actual_output="The result is 40.", tool_used="calculator", latency_ms=50.0)
    assert res_pass.passed is True

    res_fail = eval_plat.evaluate_case(case, actual_output="Wrong output", tool_used="web_search", latency_ms=50.0)
    assert res_fail.passed is False
    assert "Tool mismatch" in res_fail.failure_reason

def test_benchmark_run_and_regression_detection():
    eval_plat = EvaluationPlatform()
    cases = [
        EvaluationCase(case_id="c1", category="chat", input_prompt="Hello", expected_keywords=["Hello"]),
        EvaluationCase(case_id="c2", category="chat", input_prompt="World", expected_keywords=["World"]),
    ]

    outputs_1 = {"c1": {"output": "Hello user"}, "c2": {"output": "World user"}}
    run_1 = eval_plat.run_benchmark_suite(cases, outputs_1)
    assert run_1.pass_rate_pct == 100.0

    outputs_2 = {"c1": {"output": "Hello user"}, "c2": {"output": "Failed"}}
    run_2 = eval_plat.run_benchmark_suite(cases, outputs_2)
    assert run_2.pass_rate_pct == 50.0

    reg = eval_plat.detect_regression(baseline_run=run_1, current_run=run_2)
    assert reg["has_regression"] is True
    assert "Pass rate dropped" in reg["notes"][0]
