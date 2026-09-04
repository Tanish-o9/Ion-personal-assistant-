import asyncio
import pytest
from fastapi.testclient import TestClient

from api.main import app
from database import init_db
from orchestrator.jobs import default_job_manager

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

# ---------------------------------------------------------------------------
# 1. JobManager Lifecycle & Progress Unit Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_job_lifecycle_and_execution():
    client = TestClient(app)
    reg_res = client.post("/auth/register", json={"username": "job_user_1", "password": "jobpassword"}).json()
    user_id = reg_res["user"]["id"]

    job = default_job_manager.submit_job(user_id=user_id, session_id="session-job-1", job_type="research", payload_data="Quantum computing")
    assert job.id is not None
    assert job.status in {"pending", "running"}

    # Poll for background worker task completion (up to 3 seconds)
    completed_job = None
    for _ in range(30):
        await asyncio.sleep(0.1)
        completed_job = default_job_manager.get_job(job.id, user_id)
        if completed_job and completed_job.status in {"completed", "failed"}:
            break

    assert completed_job is not None
    assert completed_job.status == "completed"
    assert completed_job.progress == 100
    assert len(completed_job.result) > 0

@pytest.mark.asyncio
async def test_job_cancellation_and_isolation():
    client = TestClient(app)
    reg_a = client.post("/auth/register", json={"username": "job_user_a", "password": "jobpassword"}).json()
    reg_b = client.post("/auth/register", json={"username": "job_user_b", "password": "jobpassword"}).json()

    user_a_id = reg_a["user"]["id"]
    user_b_id = reg_b["user"]["id"]

    job_a = default_job_manager.submit_job(user_id=user_a_id, session_id="session-job-a", job_type="document_ingestion", payload_data="Doc A")

    # User B cannot access or cancel User A's job
    assert default_job_manager.get_job(job_a.id, user_b_id) is None
    assert default_job_manager.cancel_job(job_a.id, user_b_id) is False

    # User A cancels job
    assert default_job_manager.cancel_job(job_a.id, user_a_id) is True

# ---------------------------------------------------------------------------
# 2. REST API Background Jobs Endpoint Tests
# ---------------------------------------------------------------------------

def test_api_jobs_endpoints():
    client = TestClient(app)
    reg_res = client.post("/auth/register", json={"username": "job_api_user", "password": "jobapipassword"}).json()
    token = reg_res["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Background Job
    res_create = client.post(
        "/jobs",
        json={"session_id": "job-session-api", "job_type": "research", "payload_data": "AI multi-agent frameworks"},
        headers=headers,
    )
    assert res_create.status_code == 200
    data_create = res_create.json()
    job_id = data_create["id"]
    assert data_create["job_type"] == "research"

    # 2. List Jobs
    res_list = client.get("/jobs", headers=headers)
    assert res_list.status_code == 200
    data_list = res_list.json()
    assert len(data_list) >= 1

    # 3. Get Job Status
    res_get = client.get(f"/jobs/{job_id}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["id"] == job_id
