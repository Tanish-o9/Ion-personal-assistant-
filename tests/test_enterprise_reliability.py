import pytest
from orchestrator.reliability import default_audit_logger, default_reliability_manager
from orchestrator.jobs import default_job_manager
from database.repository import JobRepository

def test_audit_logging():
    entry = default_audit_logger.log_event(
        event_type="auth",
        user_id="u_audit_1",
        summary="User logged in successfully.",
    )
    assert entry["event_type"] == "auth"
    assert entry["user_id"] == "u_audit_1"

def test_stale_job_recovery():
    job = default_job_manager.submit_job("u_audit_2", "sess_aud", "long_task")
    JobRepository.update_job(job.id, status="running")

    # Store in memory active jobs dictionary if needed
    default_job_manager.jobs = {job.id: job}
    job.status = "running"

    recovered = default_reliability_manager.recover_stale_jobs()
    assert len(recovered) >= 1
    assert job.status == "pending"
