import pytest
from orchestrator.marketplace.publishing import (
    CapabilityPublishingEngine,
    CapabilityManifestValidator,
    RevocationManager,
    default_capability_publishing_engine,
)

def test_publisher_registration_and_submission():
    engine = CapabilityPublishingEngine()
    pub = engine.register_publisher("Acme Corp", "dev@acme.com", pub_type="VERIFIED_PARTNER")
    assert pub.publisher_id == "pub_acme_corp"

    manifest = {
        "name": "Acme Slack Connector",
        "version": "v1.0.0",
        "type": "CONNECTOR",
        "description": "Integrate Slack channels with JARVIS",
        "permissions": ["READ", "SEND"],
    }
    sub = engine.submit_capability(pub.publisher_id, manifest)
    assert sub.status == "SUBMITTED"
    assert sub.permissions_requested == ["READ", "SEND"]

def test_evaluate_and_publish_flow():
    engine = CapabilityPublishingEngine()
    pub = engine.register_publisher("Community Dev", "comm@dev.org")

    manifest = {
        "name": "Weather Skill",
        "version": "v1.2.0",
        "type": "SKILL",
        "description": "Fetch real-time weather forecasts",
        "permissions": ["READ"],
    }
    sub = engine.submit_capability(pub.publisher_id, manifest)
    published = engine.evaluate_and_publish(sub.submission_id)
    assert published.status == "PUBLISHED"
    assert published.security_score == 0.95

def test_dangerous_permission_rejection():
    engine = CapabilityPublishingEngine()
    pub = engine.register_publisher("Unverified Dev", "bad@dev.org")

    manifest = {
        "name": "Root Shell Plugin",
        "version": "v0.1",
        "type": "PLUGIN",
        "description": "Unsafe root access plugin",
        "permissions": ["ROOT_EXECUTE"],
    }
    sub = engine.submit_capability(pub.publisher_id, manifest)
    rejected = engine.evaluate_and_publish(sub.submission_id)
    assert rejected.status == "SUSPENDED"
    assert "High-risk root execution requested" in rejected.rejection_reason

def test_capability_revocation():
    rev_mgr = RevocationManager()
    res = rev_mgr.revoke_capability("market_jira_connector", "Security vulnerability patch pending")
    assert res["status"] == "REVOKED"
    assert res["user_data_preserved"] is True
