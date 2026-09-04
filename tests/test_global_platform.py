import pytest
from orchestrator.platform.localization import LocalizationManager, default_localization_manager
from orchestrator.platform.global_platform import (
    GlobalPlatformManager,
    TenantIsolationEnforcer,
    GlobalReliabilityManager,
    default_global_platform_manager,
)

def test_localization_manager():
    loc = LocalizationManager()
    assert loc.get_message("welcome", "en") == "Welcome to JARVIS 4.0"
    assert "जार्विस" in loc.get_message("welcome", "hi")
    assert loc.format_currency(100.5, "USD") == "$100.50"
    assert loc.format_currency(100.5, "INR") == "₹100.50"

def test_tenant_isolation_enforcer():
    enforcer = TenantIsolationEnforcer()
    assert enforcer.verify_access("user-1", "org-A", "ws-1", "org-A", "ws-1", "user-1") is True
    assert enforcer.verify_access("user-1", "org-A", "ws-1", "org-B", "ws-1", "user-1") is False
    assert enforcer.verify_access("user-1", "org-A", "ws-1", "org-A", "ws-2", "user-1") is False
    assert enforcer.verify_access("user-1", "org-A", "ws-1", "org-A", "ws-1", "user-2") is False

def test_global_reliability_failover():
    rel = GlobalReliabilityManager()
    avail = ["provider-a", "provider-b", "provider-c"]
    assert rel.execute_with_failover("provider-a", avail) == "provider-a"
    
    rel.mark_provider_failure("provider-a")
    assert rel.execute_with_failover("provider-a", avail) == "provider-b"

def test_global_platform_manager():
    mgr = GlobalPlatformManager()
    res = mgr.get_user_localized_response("welcome", lang="hi", currency=500.0, tz="Asia/Kolkata")
    assert res["language"] == "hi"
    assert "जार्विस" in res["message"]
    assert res["formatted_currency"] == "₹500.00"
