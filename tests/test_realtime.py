"""
Unit and Integration Tests for Phase 52: Global Knowledge & Real-Time Intelligence.
"""

import pytest
from orchestrator.realtime import (
    RealTimeManager,
    FreshnessPolicy,
    ChangeStatus,
    ChangeDetector,
)

def test_source_and_subscription_registration():
    rt = RealTimeManager()
    src = rt.register_source("Tech News Feed", "rss", "https://example.com/rss", ttl_seconds=1800)
    assert src.source_id.startswith("src_")

    sub = rt.create_subscription("user_1", "AI Developments", [src.source_id], frequency_seconds=1800)
    assert sub.subscription_id.startswith("sub_")
    assert sub.user_id == "user_1"

def test_change_detection_and_deduplication():
    rt = RealTimeManager()
    src = rt.register_source("API Docs", "web", "https://api.example.com/docs")
    sub = rt.create_subscription("user_1", "API Updates", [src.source_id])

    # First update -> NEW
    upd1 = rt.process_incoming_source_data(src.source_id, "v1 Release", "Version 1.0 released")
    assert upd1.status == ChangeStatus.NEW

    # Identical snippet -> UNCHANGED (Deduplicated)
    upd2 = rt.process_incoming_source_data(src.source_id, "v1 Release", "Version 1.0 released")
    assert upd2.status == ChangeStatus.UNCHANGED

    # Changed content -> UPDATED
    upd3 = rt.process_incoming_source_data(src.source_id, "v1.1 Patch", "Version 1.1 patch released")
    assert upd3.status == ChangeStatus.UPDATED

    # Check user notifications received for NEW and UPDATED, but not duplicate UNCHANGED
    notifs = rt.get_user_notifications("user_1")
    assert len(notifs) == 2
    assert notifs[0]["status"] == "NEW"
    assert notifs[1]["status"] == "UPDATED"

def test_freshness_policy():
    assert FreshnessPolicy.is_stale(None) is True
    assert FreshnessPolicy.is_stale("invalid-date") is True
