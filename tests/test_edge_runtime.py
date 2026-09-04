"""
Phase 88: JARVIS Edge & Local Intelligence Engine Tests.
"""

import pytest
from orchestrator.platform.edge import (
    EdgeCapability,
    PrivacyMode,
    ExecutionTarget,
    EdgeRuntime,
    default_edge_runtime
)

def test_default_lightweight_routing():
    res = default_edge_runtime.route_request(
        task_type="classification",
        privacy_mode=PrivacyMode.DEFAULT
    )
    assert res.target == ExecutionTarget.LOCAL
    assert res.selected_model == "rule_classifier_v1"
    assert res.cost_estimate_usd == 0.0

def test_local_only_privacy_mode_enforcement():
    # Register local LLM capability
    runtime = EdgeRuntime()
    runtime.register_capability(EdgeCapability.LOCAL_LLM, "ollama_llama3_8b")

    res = runtime.route_request(
        task_type="llm",
        privacy_mode=PrivacyMode.LOCAL_ONLY
    )
    assert res.target == ExecutionTarget.LOCAL
    assert res.selected_model == "ollama_llama3_8b"

def test_local_only_mode_blocks_remote_fallback_when_missing():
    runtime = EdgeRuntime()  # No local LLM registered

    res = runtime.route_request(
        task_type="llm",
        privacy_mode=PrivacyMode.LOCAL_ONLY
    )
    assert res.target == ExecutionTarget.BLOCKED
    assert "Remote fallback prohibited" in res.reason

def test_offline_mode_behavior():
    runtime = EdgeRuntime()
    runtime.set_connectivity(is_online=False)

    res = runtime.route_request(
        task_type="complex_analysis",
        privacy_mode=PrivacyMode.DEFAULT
    )
    assert res.target == ExecutionTarget.BLOCKED
    assert "offline" in res.reason.lower()
