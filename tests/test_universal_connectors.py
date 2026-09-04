"""
Unit Tests for Phase 70: Universal Connector Platform.
"""

import pytest
from database.connection import init_db
from orchestrator.connectors.platform import UniversalConnectorSDK
from orchestrator.connectors.models import PermissionScope

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def test_connector_registration_credentials_and_idempotency():
    sdk = UniversalConnectorSDK()
    user_id = "user_conn_plat_1"

    # Register
    desc = sdk.register_connector_definition(
        name="GitHub Connector",
        provider="GitHub",
        capabilities=["read_repo", "create_issue"],
        permissions=[PermissionScope.READ, PermissionScope.CREATE],
        risk_level="LOW"
    )
    assert desc.connector_id.startswith("conn_")

    # Store credentials
    assert sdk.store_credentials(desc.connector_id, user_id, "ghp_secrettoken1234567890") is True

    # Execute low-risk operation
    res1 = sdk.execute_connector_operation(
        desc.connector_id,
        user_id,
        "create",
        {"title": "Bug fix"},
        idempotency_key="idempotent_key_1"
    )
    assert res1["status"] == "success"

    # Repeat with same idempotency key -> Returns cached result
    res2 = sdk.execute_connector_operation(
        desc.connector_id,
        user_id,
        "create",
        {"title": "Bug fix"},
        idempotency_key="idempotent_key_1"
    )
    assert res2["status"] == "success"

def test_high_risk_universal_connector_approval():
    sdk = UniversalConnectorSDK()
    user_id = "user_conn_plat_2"

    desc = sdk.register_connector_definition(
        name="Slack Connector",
        provider="Slack",
        capabilities=["send_channel_message"],
        permissions=[PermissionScope.SEND],
        risk_level="HIGH"
    )

    res = sdk.execute_connector_operation(desc.connector_id, user_id, "send", {"channel": "#general", "text": "Announcement"})
    assert res["status"] == "WAITING_FOR_APPROVAL"
    assert "approval_id" in res
