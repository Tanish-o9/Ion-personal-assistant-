import pytest
from orchestrator.resources import ResourceManager, ResourceLimits

def test_resource_usage_and_cost_calculation():
    mgr = ResourceManager()
    usage = mgr.record_usage("u_res_1", model_name="gpt-4o", input_tokens=1000, output_tokens=500, tool_calls=2)

    assert usage.total_tokens == 1500
    assert usage.llm_calls == 1
    assert usage.tool_calls == 2
    assert usage.estimated_cost_usd > 0.0

def test_budget_soft_warning_and_hard_limit():
    limits = ResourceLimits(max_tokens=1000, max_llm_calls=10)
    mgr = ResourceManager(default_limits=limits)

    # Under 80% -> allow
    mgr.record_usage("u_res_2", input_tokens=500, output_tokens=0)
    status_allow = mgr.check_budget("u_res_2")
    assert status_allow.action == "allow"

    # 80%+ -> soft warning
    mgr.record_usage("u_res_2", input_tokens=350, output_tokens=0) # 850 total
    status_warn = mgr.check_budget("u_res_2")
    assert status_warn.action == "soft_warning"
    assert status_warn.warning_issued is True

    # 100%+ -> hard limit block
    mgr.record_usage("u_res_2", input_tokens=200, output_tokens=0) # 1050 total
    status_block = mgr.check_budget("u_res_2")
    assert status_block.action == "hard_limit_block"
    assert status_block.limit_exceeded is True
