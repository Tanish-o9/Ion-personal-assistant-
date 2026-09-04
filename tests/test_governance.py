"""
Unit and Adversarial Security Tests for Phase 51: Advanced Security, Privacy & Data Governance.
"""

import pytest
from datetime import datetime, timedelta
from orchestrator.security.governance import (
    DataClassification,
    DataClassificationPolicy,
    DataAccessPolicy,
    PrivacyManager,
    SecretProtector,
    DataRetentionPolicyManager,
    PrivacyAwareLogger,
)

def test_data_classification():
    assert DataClassificationPolicy.classify_source("web_search") == DataClassification.PUBLIC
    assert DataClassificationPolicy.classify_source("api_key") == DataClassification.SECRET
    assert DataClassificationPolicy.classify_source("user_chat") == DataClassification.PRIVATE
    assert DataClassificationPolicy.classify_source("profile_health") == DataClassification.SENSITIVE
    assert DataClassificationPolicy.classify_source("system_log") == DataClassification.INTERNAL

def test_data_access_policy():
    # User A accessing User A's data
    assert DataAccessPolicy.authorize_access("user_1", "user_1", classification=DataClassification.PRIVATE) is True

    # User A accessing User B's private data -> DENIED
    assert DataAccessPolicy.authorize_access("user_1", "user_2", classification=DataClassification.PRIVATE) is False

    # Secret data: User A accessing User B's secret -> DENIED even for Admin
    assert DataAccessPolicy.authorize_access("admin", "user_2", classification=DataClassification.SECRET, is_admin=True) is False

    # Workspace sharing for PUBLIC/INTERNAL data
    assert DataAccessPolicy.authorize_access("user_1", "user_2", requesting_workspace_id="ws1", resource_workspace_id="ws1", classification=DataClassification.PUBLIC) is True
    assert DataAccessPolicy.authorize_access("user_1", "user_2", requesting_workspace_id="ws1", resource_workspace_id="ws2", classification=DataClassification.PUBLIC) is False

def test_privacy_manager():
    pm = PrivacyManager()
    assert pm.is_feature_enabled("u1", "memory") is True
    res = pm.process_privacy_request("u1", "disable", "memory")
    assert res["enabled"] is False
    assert pm.is_feature_enabled("u1", "memory") is False

    res_enable = pm.process_privacy_request("u1", "enable", "memory")
    assert res_enable["enabled"] is True
    assert pm.is_feature_enabled("u1", "memory") is True

def test_secret_protection():
    sp = SecretProtector()
    raw = "Here is my key: sk-abc123456789012345678901234567890 and DB postgres://user:pass@localhost:5432/db"
    redacted = sp.redact_secrets(raw)
    assert "[REDACTED_SECRET]" in redacted
    assert "sk-abc" not in redacted
    assert "postgres://" not in redacted

def test_data_retention_policy():
    ret = DataRetentionPolicyManager(custom_retention={"logs": 10})
    now = datetime.utcnow()
    old_date = now - timedelta(days=15)
    recent_date = now - timedelta(days=5)

    assert ret.is_expired("logs", old_date) is True
    assert ret.is_expired("logs", recent_date) is False

def test_privacy_aware_logger():
    logger = PrivacyAwareLogger()
    log = logger.format_log(
        request_id="req_123",
        session_id="sess_456",
        status="success",
        message="User requested sk-secretkey12345678901234567890",
        user_content="Private email context"
    )
    assert log["request_id"] == "req_123"
    assert "[REDACTED_SECRET]" in log["message"]
    assert "sk-secretkey" not in log["message"]
