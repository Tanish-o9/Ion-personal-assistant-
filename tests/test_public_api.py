import pytest
from orchestrator.sdk.auth import default_api_key_manager
from orchestrator.sdk.public_api import (
    PublicAPIGateway,
    PublicAPIRequest,
    default_public_api_gateway,
)
from orchestrator.sdk.errors import (
    AuthenticationError,
    AuthorizationError,
    ValidationError,
)

def test_public_api_chat_and_research_endpoints():
    raw_key, _ = default_api_key_manager.create_api_key("usr-10", ["chat:write", "research:execute"])
    gateway = PublicAPIGateway()

    req_chat = PublicAPIRequest(
        api_key=raw_key,
        endpoint="/api/v1/chat",
        scopes_required=["chat:write"],
        user_id="usr-10",
        org_id="org_default",
        workspace_id="ws_default",
        payload={"message": "Hello public API"},
    )
    res_chat = gateway.handle_request("/api/v1/chat", req_chat)
    assert res_chat.status_code == 200
    assert res_chat.api_version == "v1"

    req_res = PublicAPIRequest(
        api_key=raw_key,
        endpoint="/api/v1/research",
        scopes_required=["research:execute"],
        user_id="usr-10",
        org_id="org_default",
        workspace_id="ws_default",
        payload={"query": "AI research"},
    )
    res_res = gateway.handle_request("/api/v1/research", req_res)
    assert res_res.status_code == 200

def test_public_api_scope_denial():
    raw_key, _ = default_api_key_manager.create_api_key("usr-11", ["chat:read"])  # Missing chat:write
    gateway = PublicAPIGateway()

    req = PublicAPIRequest(
        api_key=raw_key,
        endpoint="/api/v1/chat",
        scopes_required=["chat:write"],
        user_id="usr-11",
        org_id="org_default",
        workspace_id="ws_default",
    )
    with pytest.raises(AuthorizationError):
        gateway.handle_request("/api/v1/chat", req)

def test_public_api_invalid_endpoint():
    raw_key, _ = default_api_key_manager.create_api_key("usr-12", ["*"])
    gateway = PublicAPIGateway()

    req = PublicAPIRequest(
        api_key=raw_key,
        endpoint="/api/v1/nonexistent",
        scopes_required=[],
        user_id="usr-12",
    )
    with pytest.raises(ValidationError):
        gateway.handle_request("/api/v1/nonexistent", req)
