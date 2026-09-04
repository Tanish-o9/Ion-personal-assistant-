"""
Unit Tests for Phase 57: JARVIS Internet & Service Connectors.
"""

import pytest
from typing import Dict, Any, Optional
from orchestrator.connectors import (
    BaseConnector,
    ConnectorDescriptor,
    PermissionScope,
    ConnectorRegistry,
)

class MockCalendarConnector(BaseConnector):
    def __init__(self, risk_level: str = "LOW"):
        desc = ConnectorDescriptor(
            connector_id="mock_calendar",
            name="Google Calendar",
            provider="Google",
            capabilities=["read_events", "create_event"],
            required_scopes=[PermissionScope.READ, PermissionScope.CREATE],
            risk_level=risk_level
        )
        super().__init__(desc)

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        self._authenticated = True
        return True

    def read(self, resource_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"event_id": resource_id, "summary": "Team Sync"}

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"event_id": "evt_99", "status": "created"}

    def update(self, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"event_id": resource_id, "updated": True}

    def delete(self, resource_id: str) -> bool:
        return True

def test_connector_registration_and_read():
    reg = ConnectorRegistry()
    conn = MockCalendarConnector(risk_level="LOW")
    conn.authenticate({"token": "secret_token"})
    reg.register_connector(conn)

    assert len(reg.list_connectors()) == 1
    res = reg.execute_action("mock_calendar", "user_1", "read", {}, resource_id="evt_123")
    assert res["status"] == "success"
    assert res["result"]["summary"] == "Team Sync"

def test_high_risk_action_requires_approval():
    reg = ConnectorRegistry()
    conn = MockCalendarConnector(risk_level="HIGH")
    conn.authenticate({"token": "secret_token"})
    reg.register_connector(conn)

    res = reg.execute_action("mock_calendar", "user_1", "create", {"summary": "New Event"})
    assert res["status"] == "WAITING_FOR_APPROVAL"
    assert "approval_id" in res
