"""
Unit Tests for Phase 58: Enterprise Workspace 2.0.
"""

import pytest
from database.connection import init_db
from orchestrator.workspaces import OrganizationManager, default_workspace_manager

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def test_organization_creation_and_policy_compliance():
    om = OrganizationManager()
    user_id = "org_owner_1"

    org = om.create_organization(
        owner_id=user_id,
        name="Enterprise Corp",
        policies={"allowed_models": ["gpt-4o"], "maximum_budget_usd": 50.0}
    )
    assert org["id"].startswith("org_")
    assert org["name"] == "Enterprise Corp"

    # Fetch org
    fetched = om.get_organization(org["id"], user_id)
    assert fetched is not None
    assert fetched["name"] == "Enterprise Corp"

    # Validate model & budget policies
    assert om.validate_policy_compliance(org["id"], "gpt-4o", requested_budget=10.0) is True
    assert om.validate_policy_compliance(org["id"], "forbidden-model", requested_budget=10.0) is False
    assert om.validate_policy_compliance(org["id"], "gpt-4o", requested_budget=100.0) is False

def test_organization_workspace_binding():
    om = OrganizationManager()
    owner_id = "org_owner_2"
    org = om.create_organization(owner_id=owner_id, name="Tech Org")
    ws = default_workspace_manager.create_workspace(name="Dev Workspace", owner_id=owner_id)

    bound = om.add_workspace_to_org(ws.id, org["id"], owner_id)
    assert bound is True
