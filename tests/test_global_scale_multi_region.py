import pytest
from orchestrator.platform.global_routing import (
    Region, RegionRegistry, RegionRouter, GlobalLLMRouter, GlobalJobRouter,
    GlobalSchedulerSafety, WebSocketSessionManager, GlobalFailoverEngine,
    default_region_registry
)

def test_region_routing():
    router = RegionRouter(default_region_registry)
    # Match user region
    res1 = router.select_region(user_region="us-west-2")
    assert res1 == "us-west-2"

    # Enforce data residency
    res2 = router.select_region(user_region="us-west-2", workspace_residency_policy="eu-central-1")
    assert res2 == "eu-central-1"

def test_data_residency_violation():
    router = RegionRouter(default_region_registry)
    with pytest.raises(PermissionError):
        router.select_region(user_region="us-west-2", workspace_residency_policy="invalid-region")

def test_global_llm_routing():
    router = RegionRouter(default_region_registry)
    llm_router = GlobalLLMRouter(router)
    res = llm_router.route_llm_request(model="jarvis-v5", user_region="eu-central-1")
    assert res["target_region"] == "eu-central-1"
    assert res["routed"] is True

def test_global_job_routing():
    router = RegionRouter(default_region_registry)
    job_router = GlobalJobRouter(router)
    res = job_router.route_job(
        job_id="job-101",
        user_region="us-east-1",
        allowed_regions=["eu-central-1"]
    )
    assert res["execution_region"] == "eu-central-1"

def test_global_scheduler_safety():
    safety = GlobalSchedulerSafety()
    # Acquire lease
    assert safety.acquire_lease("cron-1", "us-east-1") is True
    # Duplicate lease attempt from another region should fail
    assert safety.acquire_lease("cron-1", "us-west-2") is False

    # Release lease and re-acquire
    safety.release_lease("cron-1", "us-east-1")
    assert safety.acquire_lease("cron-1", "us-west-2") is True

def test_global_failover():
    reg = RegionRegistry()
    failover = GlobalFailoverEngine(reg)
    new_region = failover.trigger_failover("us-east-1")
    assert new_region != "us-east-1"
    assert reg.get_region("us-east-1").status == "OFFLINE"
