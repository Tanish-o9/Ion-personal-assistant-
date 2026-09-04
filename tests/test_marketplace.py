"""
Unit Tests for Phase 61: Capability Marketplace 2.0.
"""

import pytest
from orchestrator.marketplace import (
    MarketplaceManager,
    CapabilityCategory,
)

def test_marketplace_discovery_and_evaluation():
    mm = MarketplaceManager()

    # Discover
    connectors = mm.discover_capabilities(category=CapabilityCategory.CONNECTOR)
    assert len(connectors) == 1
    assert connectors[0].id == "market_jira_connector"

    # Evaluate
    eval_res = mm.evaluate_capability("market_jira_connector")
    assert eval_res["status"] == "APPROVED"
    assert eval_res["evaluation_score"] >= 0.8

def test_marketplace_installation_and_rollback():
    mm = MarketplaceManager()
    user_id = "user_mkt_1"
    cap_id = "market_code_reviewer"

    # Install v1.0.0
    res_inst = mm.install_capability(cap_id, user_id)
    assert res_inst["status"] == "installed"
    assert res_inst["capability"].is_installed is True

    # Upgrade to v1.1.0
    mm._catalog[cap_id].version = "1.1.0"
    mm.install_capability(cap_id, user_id)

    # Rollback to v1.0.0
    res_roll = mm.rollback_capability(cap_id)
    assert res_roll["status"] == "rolled_back"
    assert res_roll["previous_version"] == "1.0.0"
