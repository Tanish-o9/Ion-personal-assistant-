"""
Unit and Integration Tests for Phase 54: JARVIS Edge / Offline / Resilient Client Capabilities.
"""

import pytest
from orchestrator.offline import (
    EdgeOfflineManager,
    NetworkStatus,
    PrivacyMode,
    OfflineSyncManager,
    QueuedOfflineAction,
    SyncConflictStatus,
)

def test_capability_matrix_online_vs_offline():
    mgr = EdgeOfflineManager()

    # Online status
    assert mgr.is_capability_available("cloud_web_research") is True
    assert mgr.is_capability_available("local_file_reading") is True

    # Switch to OFFLINE
    mgr.set_network_status(NetworkStatus.OFFLINE)
    assert mgr.is_capability_available("cloud_web_research") is False
    assert mgr.is_capability_available("local_file_reading") is True

def test_privacy_mode_gateway_routing():
    mgr = EdgeOfflineManager()

    # Default -> cloud_provider
    assert mgr.resolve_provider_route(is_cloud_available=True) == "cloud_provider"

    # Local preferred -> local_provider
    mgr.set_privacy_mode(PrivacyMode.LOCAL_PREFERRED)
    assert mgr.resolve_provider_route(is_cloud_available=True) == "local_provider"

    # Local only -> local_provider
    mgr.set_privacy_mode(PrivacyMode.LOCAL_ONLY)
    assert mgr.resolve_provider_route(is_cloud_available=True) == "local_provider"

def test_offline_queue_and_conflict_resolution():
    sync = OfflineSyncManager()
    action = QueuedOfflineAction(
        action_id="act_1",
        user_id="user_1",
        capability_name="local_file_reading",
        payload={"file": "doc.txt"},
        timestamp_iso="2026-09-04T05:00:00Z"
    )
    sync.enqueue_action(action)
    queued = sync.get_queued_actions("user_1")
    assert len(queued) == 1
    assert queued[0].action_id == "act_1"

    # Detect conflicts
    status1 = sync.detect_conflict(local_version=2, local_timestamp="t2", remote_version=1, remote_timestamp="t1")
    assert status1 == SyncConflictStatus.LOCAL_NEWER

    status2 = sync.detect_conflict(local_version=1, local_timestamp="t1", remote_version=2, remote_timestamp="t2")
    assert status2 == SyncConflictStatus.REMOTE_NEWER
