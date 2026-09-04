"""
Phase 89: Device Security, Permissions & Safety Layer Tests.
"""

import pytest
from orchestrator.devices.models import DeviceType, DeviceCapability
from orchestrator.devices.registry import default_device_registry
from orchestrator.devices.security import DeviceSecurityPolicy, default_device_security_policy
from database.connection import get_db_context
from database.models import UserModel

@pytest.fixture(autouse=True)
def setup_test_user():
    with get_db_context() as db:
        user = db.query(UserModel).filter_by(id="test_sec_user").first()
        if not user:
            user = UserModel(id="test_sec_user", username="sec_user", password_hash="hash")
            db.add(user)
            db.commit()

def test_secret_redaction_guard():
    raw_payload = {
        "device_id": "dev_123",
        "api_key": "secret_token_abc123",
        "nested": {"password": "my_password_999", "status": "ONLINE"}
    }
    redacted = DeviceSecurityPolicy.redact_secrets(raw_payload)
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["nested"]["password"] == "[REDACTED]"
    assert redacted["nested"]["status"] == "ONLINE"

def test_unauthorized_user_blocked():
    dev = default_device_registry.register_device(
        user_id="test_sec_user",
        name="Security Camera",
        device_type=DeviceType.CAMERA_STATUS_ONLY,
        capabilities=[DeviceCapability.READ_STATUS]
    )

    auth, risk, req_app, app_id = default_device_security_policy.authorize_and_audit(
        user_id="unauthorized_attacker",
        device=dev,
        capability=DeviceCapability.READ_STATUS,
        parameters={}
    )

    assert auth is False
    assert risk == "BLOCKED"
    assert req_app is False

def test_high_risk_action_triggers_approval_request():
    dev = default_device_registry.register_device(
        user_id="test_sec_user",
        name="Critical Server Switch",
        device_type=DeviceType.SMART_PLUG,
        capabilities=[DeviceCapability.SET_STATE]
    )

    auth, risk, req_app, app_id = default_device_security_policy.authorize_and_audit(
        user_id="test_sec_user",
        device=dev,
        capability=DeviceCapability.SET_STATE,
        parameters={"power": "OFF", "scope": "CRITICAL"}
    )

    assert auth is False
    assert risk == "HIGH"
    assert req_app is True
    assert app_id is not None
    assert isinstance(app_id, str)

