import pytest
import hmac
import hashlib
from orchestrator.sdk import default_api_key_manager, JARVISClient
from orchestrator.sdk.errors import (
    AuthenticationError,
    AuthorizationError,
    ValidationError,
)

def test_sdk_auth_and_chat():
    raw_key, key_model = default_api_key_manager.create_api_key("dev-1", ["chat:write", "research:execute", "workflows:execute", "capabilities:read"])
    client = JARVISClient(api_key=raw_key)
    
    res = client.chat("Hello from SDK 2.0")
    assert res.status == "success"
    assert "JARVIS SDK Response" in res.response

def test_sdk_authorization_failure():
    raw_key, _ = default_api_key_manager.create_api_key("dev-2", ["chat:read"])  # Lacks research scope
    client = JARVISClient(api_key=raw_key)

    with pytest.raises(AuthorizationError):
        client.research("Quantum computing")

def test_sdk_invalid_key_authentication():
    client = JARVISClient(api_key="jrv_invalid_key_123")
    with pytest.raises(AuthenticationError):
        client.chat("Hello")

def test_sdk_idempotency_retries():
    raw_key, _ = default_api_key_manager.create_api_key("dev-3", ["workflows:execute"])
    client = JARVISClient(api_key=raw_key)

    wf1 = client.execute_workflow("wf-100", {"param": 1}, idempotency_key="idemp-key-1")
    assert wf1.status == "COMPLETED"

    wf2 = client.execute_workflow("wf-100", {"param": 1}, idempotency_key="idemp-key-1")
    assert wf2.status == "COMPLETED_IDEMPOTENT_REUSE"

def test_sdk_webhook_verification():
    raw_key, _ = default_api_key_manager.create_api_key("dev-4", ["*"])
    client = JARVISClient(api_key=raw_key, webhook_secret="secret_test_123")
    
    payload = {"event_type": "workflow_completed", "id": "123"}
    payload_str = str(payload).encode("utf-8")
    valid_sig = hmac.new(b"secret_test_123", payload_str, hashlib.sha256).hexdigest()

    event = client.process_webhook_event(payload, valid_sig)
    assert event["processed"] is True

    with pytest.raises(AuthenticationError):
        client.process_webhook_event(payload, "invalid_sig_123")
