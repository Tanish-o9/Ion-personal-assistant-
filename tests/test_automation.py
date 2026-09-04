import pytest
from orchestrator.automation import default_automation_manager
from orchestrator.auth import default_user_store, hash_password, create_token
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

@pytest.fixture
def test_user_and_token():
    u_name = "auto_user_test"
    u = default_user_store.get_by_username(u_name)
    if not u:
        u = default_user_store.register_user(username=u_name, password_hash=hash_password("Pass123!"))
    token = create_token(user_id=u.id, username=u.username)
    return u, token

def test_automation_manager_lifecycle(test_user_and_token):
    user, _ = test_user_and_token

    # 1. Create automation
    auto = default_automation_manager.create_automation(
        user_id=user.id,
        name="Weekly Research Summary",
        workflow_text="Research latest AI news every Monday",
        schedule_cron="0 9 * * 1",
    )
    assert auto["name"] == "Weekly Research Summary"
    assert auto["enabled"] is True

    # 2. List automations
    autos = default_automation_manager.list_automations(user_id=user.id)
    assert len(autos) >= 1

    # 3. Pause & Resume
    assert default_automation_manager.pause_automation(auto["id"], user.id) is True
    updated = default_automation_manager.get_automation(auto["id"], user.id)
    assert updated["enabled"] is False

    assert default_automation_manager.resume_automation(auto["id"], user.id) is True

    # 4. Trigger manual execution
    run_res = default_automation_manager.run_automation(auto["id"], user.id)
    assert run_res is not None
    assert run_res["status"] == "running"
    assert "job_id" in run_res

    # 5. Delete automation
    assert default_automation_manager.delete_automation(auto["id"], user.id) is True

def test_automation_api_endpoints(test_user_and_token):
    user, token = test_user_and_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create via API
    resp = client.post(
        "/automations",
        json={
            "name": "Daily Health Check",
            "workflow_text": "Check system metrics daily",
            "schedule_cron": "0 8 * * *",
            "timezone": "UTC",
        },
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    auto_id = data["id"]
    assert data["name"] == "Daily Health Check"

    # List via API
    list_resp = client.get("/automations", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # Run via API
    run_resp = client.post(f"/automations/{auto_id}/run", headers=headers)
    assert run_resp.status_code == 200
    assert "job_id" in run_resp.json()

    # Delete via API
    del_resp = client.delete(f"/automations/{auto_id}", headers=headers)
    assert del_resp.status_code == 200
