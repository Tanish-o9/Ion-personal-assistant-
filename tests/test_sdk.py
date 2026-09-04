import pytest
from orchestrator.sdk import default_api_key_manager, JarvisSDKClient
from orchestrator.sdk.errors import AuthenticationError

def test_api_key_generation_and_validation():
    raw_key, model = default_api_key_manager.create_api_key("u_sdk_1", scopes=["chat:write", "research:execute"])
    assert raw_key.startswith("jrv_")

    val_ok = default_api_key_manager.validate_key(raw_key, "chat:write")
    assert val_ok is not None

    val_no_scope = default_api_key_manager.validate_key(raw_key, "documents:write")
    assert val_no_scope is None

def test_sdk_client_chat():
    raw_key, _ = default_api_key_manager.create_api_key("u_sdk_2", scopes=["chat:write"])
    client = JarvisSDKClient(api_key=raw_key)

    res = client.chat("Hello from SDK")
    assert res["status"] == "success"
    assert "JARVIS SDK Response" in res["response"]

    # Invalid key fails
    bad_client = JarvisSDKClient(api_key="jrv_invalid")
    with pytest.raises((PermissionError, AuthenticationError)):
        bad_client.chat("Test")
