import pytest
from fastapi.testclient import TestClient

from api.main import app
from orchestrator.observability import (
    sanitize_data,
    default_metrics,
)
from orchestrator.tools import default_executor

# ---------------------------------------------------------------------------
# 1. Privacy Sanitization Unit Tests
# ---------------------------------------------------------------------------

def test_sensitive_data_sanitization():
    payload = {
        "username": "alice",
        "password": "SuperSecretPassword123!",
        "token": "bearer.token.123",
        "nested": {
            "api_key": "sk-123456",
            "safe_field": "public_data",
        },
    }

    sanitized = sanitize_data(payload)
    assert sanitized["username"] == "alice"
    assert sanitized["password"] == "[REDACTED]"
    assert sanitized["token"] == "[REDACTED]"
    assert sanitized["nested"]["api_key"] == "[REDACTED]"
    assert sanitized["nested"]["safe_field"] == "public_data"

# ---------------------------------------------------------------------------
# 2. Health & Readiness API Endpoint Tests
# ---------------------------------------------------------------------------

def test_health_and_readiness_endpoints():
    client = TestClient(app)

    # 1. Liveness probe /health
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    # 2. Readiness probe /ready
    res_ready = client.get("/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] in {"ready", "degraded"}
    assert "database" in res_ready.json()

# ---------------------------------------------------------------------------
# 3. Request Tracing & Metrics Endpoints Tests
# ---------------------------------------------------------------------------

def test_request_tracing_middleware_and_metrics_endpoint():
    client = TestClient(app)

    # 1. Request ID header propagation
    res = client.get("/health", headers={"X-Request-ID": "req_test_12345"})
    assert res.status_code == 200
    assert res.headers.get("X-Request-ID") == "req_test_12345"

    # 2. Auto-generated Request ID header if missing
    res_auto = client.get("/health")
    assert res_auto.status_code == 200
    assert res_auto.headers.get("X-Request-ID").startswith("req_")

    # 3. Prometheus /metrics endpoint
    res_metrics = client.get("/metrics")
    assert res_metrics.status_code == 200
    assert "jarvis_requests_total" in res_metrics.text
    assert "jarvis_llm_requests_total" in res_metrics.text

# ---------------------------------------------------------------------------
# 4. Tool & Monitoring Summary Tests
# ---------------------------------------------------------------------------

def test_tool_observability_and_summary_endpoint():
    client = TestClient(app)

    # Execute a tool to populate metrics
    default_executor.execute("calculator", operation="add", a=10, b=20)

    # Register/login user to access /monitoring/summary
    reg_res = client.post("/auth/register", json={"username": "obs_user", "password": "obspassword"}).json()
    token = reg_res["token"]

    res_summary = client.get("/monitoring/summary", headers={"Authorization": f"Bearer {token}"})
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert "metrics" in summary
    assert summary["metrics"]["tools"]["total_calls"] >= 1
    assert "calculator" in summary["metrics"]["tools"]["by_tool"]
