import pytest
from orchestrator.platform.jarvis_5_integration import (
    UnifiedRequestLifecycleManager, UnifiedCapabilityLifecycle,
    UnifiedSecurityBoundary, UnifiedObservabilityTrace, CapabilityStage
)

def test_unified_request_lifecycle():
    manager = UnifiedRequestLifecycleManager()
    res = manager.execute_request_pipeline(
        user_id="user-master",
        session_id="session-master",
        prompt="Analyze revenue report and adjust living room thermostat",
        organization_id="org-master",
        workspace_id="ws-master",
    )
    assert res["status"] == "COMPLETED"
    assert len(res["stages_executed"]) == 16
    assert "AUTHENTICATION" in res["stages_executed"]
    assert "SECURITY_POLICY" in res["stages_executed"]

def test_unified_capability_lifecycle():
    cap = UnifiedCapabilityLifecycle()
    res = cap.transition_capability("custom_connector", CapabilityStage.VALIDATE)
    assert res["current_stage"] == "VALIDATE"
    assert res["status"] == "SUCCESS"

def test_unified_security_boundary():
    sec = UnifiedSecurityBoundary()
    res = sec.verify_request_security("u1", "org1", "device_control", risk_level="HIGH")
    assert res["security_verified"] is True
    assert res["approval_status"] == "WAITING_FOR_APPROVAL"

def test_unified_observability_trace():
    trace = UnifiedObservabilityTrace()
    trace.add_span("LLM_GATEWAY", 45.2, {"model": "ion-v5"})
    trace.add_span("TOOL_EXECUTION", 12.1, {"tool": "device_light"})
    res = trace.export_trace()
    assert res["total_spans"] == 2
    assert res["trace_status"] == "OK"
