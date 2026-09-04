import pytest
from orchestrator.auth.enterprise_policy import (
    EnterpriseRole, EnterprisePolicy, EnterprisePolicyManager,
    MultiTierBudgetManager, EnterpriseResourceOwnershipManager, EnterpriseAuditLogger
)

def test_enterprise_policy_management():
    manager = EnterprisePolicyManager()
    policy = EnterprisePolicy(
        organization_id="org-1",
        workspace_id="ws-1",
        allowed_models=["gpt-4o", "jarvis-v5"],
        max_monthly_budget_usd=1000.0,
    )
    manager.set_policy(policy)

    eff = manager.get_effective_policy("org-1", "ws-1")
    assert eff.max_monthly_budget_usd == 1000.0
    assert manager.validate_capability_access("org-1", "ws-1", "chat", model_name="gpt-4o") is True
    assert manager.validate_capability_access("org-1", "ws-1", "chat", model_name="unauthorized-model") is False

def test_multi_tier_budget_inheritance():
    policy_mgr = EnterprisePolicyManager()
    policy_mgr.set_policy(EnterprisePolicy(organization_id="org-1", max_monthly_budget_usd=100.0))
    budget_mgr = MultiTierBudgetManager(policy_mgr)

    budget_mgr.record_usage("org-1", 50.0)
    assert budget_mgr.validate_budget("org-1", None, 40.0) is True

    with pytest.raises(PermissionError):
        budget_mgr.validate_budget("org-1", None, 60.0)

def test_enterprise_resource_ownership():
    ownership = EnterpriseResourceOwnershipManager()
    # Same tenant
    assert ownership.validate_resource_access(
        user_role=EnterpriseRole.MEMBER,
        resource_org_id="org-1",
        resource_workspace_id="ws-1",
        user_org_id="org-1",
        user_workspace_id="ws-1",
    ) is True

    # Cross-tenant org access raises error
    with pytest.raises(PermissionError):
        ownership.validate_resource_access(
            user_role=EnterpriseRole.MEMBER,
            resource_org_id="org-2",
            resource_workspace_id="ws-1",
            user_org_id="org-1",
            user_workspace_id="ws-1",
        )

def test_enterprise_audit_logger():
    logger = EnterpriseAuditLogger()
    logger.log_event(
        organization_id="org-1",
        workspace_id="ws-1",
        user_id="u1",
        event_type="POLICY_CHANGE",
        resource_type="policy",
        resource_id="pol-1",
        action="UPDATE",
    )
    assert len(logger.events) == 1
    assert logger.events[0]["action"] == "UPDATE"
