import pytest
from orchestrator.platform import default_capability_registry, default_platform_lifecycle

def test_unified_capability_discovery():
    caps = default_capability_registry.search_capabilities("calculator")
    assert "calculator" in caps["tools"]

    agent_caps = default_capability_registry.search_capabilities("research")
    assert "ResearchAgent" in agent_caps["agents"] or "research_skill" in agent_caps["skills"]

def test_platform_lifecycle_execution():
    res = default_platform_lifecycle.process_request(
        user_id="user_plat_1",
        session_id="sess_plat_1",
        raw_text="What is the weather in Delhi?",
    )
    assert res["status"] == "success"
    assert res["prompt_injection_detected"] is False
