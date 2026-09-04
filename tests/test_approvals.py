import pytest
from orchestrator.approval import default_approval_manager, ApprovalPolicyEvaluator
from orchestrator.auth import default_user_store, hash_password, create_token
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

@pytest.fixture
def test_user_and_token():
    u_name = "approval_user_test"
    u = default_user_store.get_by_username(u_name)
    if not u:
        u = default_user_store.register_user(username=u_name, password_hash=hash_password("Pass123!"))
    token = create_token(user_id=u.id, username=u.username)
    return u, token

def test_approval_policy_evaluator():
    # Low risk -> no approval
    assert ApprovalPolicyEvaluator.requires_approval("read_file", risk_level="low") is False

    # High risk or restricted -> requires approval
    assert ApprovalPolicyEvaluator.requires_approval("system_delete", risk_level="high") is True
    assert ApprovalPolicyEvaluator.requires_approval("database_drop", risk_level="medium") is True
    assert ApprovalPolicyEvaluator.requires_approval("custom", requires_confirmation=True) is True

def test_approval_manager_lifecycle(test_user_and_token):
    user, _ = test_user_and_token

    # 1. Create approval request
    appr = default_approval_manager.create_approval(
        user_id=user.id,
        session_id="session-appr-1",
        action_type="database_drop",
        action_summary="Drop production backup table",
        risk_level="high",
    )
    assert appr["status"] == "pending"
    assert appr["risk_level"] == "high"

    # 2. List pending approvals
    pending = default_approval_manager.list_approvals(user.id, status_filter="pending")
    assert len(pending) >= 1

    # 3. Approve request
    assert default_approval_manager.approve(appr["id"], user.id) is True
    updated = default_approval_manager.get_approval(appr["id"], user.id)
    assert updated["status"] == "approved"
    assert updated["resolved_by"] == user.id

def test_approval_rejection_and_isolation(test_user_and_token):
    user, _ = test_user_and_token

    appr = default_approval_manager.create_approval(
        user_id=user.id,
        session_id="session-appr-2",
        action_type="network_modify",
        action_summary="Modify firewall rule",
        risk_level="high",
    )

    # Reject request
    assert default_approval_manager.reject(appr["id"], user.id) is True
    updated = default_approval_manager.get_approval(appr["id"], user.id)
    assert updated["status"] == "rejected"

    # User isolation check: User B cannot approve User A's approval
    assert default_approval_manager.approve(appr["id"], "other_user_id") is False

def test_approval_api_endpoints(test_user_and_token):
    user, token = test_user_and_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create approval manually in manager
    appr = default_approval_manager.create_approval(
        user_id=user.id,
        session_id="session-appr-api",
        action_type="system_delete",
        action_summary="Delete directory",
        risk_level="high",
    )

    # List via API
    resp = client.get("/approvals", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    # Approve via API
    appr_resp = client.post(f"/approvals/{appr['id']}/approve", headers=headers)
    assert appr_resp.status_code == 200
    assert appr_resp.json()["approved_id"] == appr["id"]
