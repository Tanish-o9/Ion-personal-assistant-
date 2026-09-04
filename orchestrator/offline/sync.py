"""
Phase 54: Offline Queue & Sync Manager with Conflict Detection.
"""

from typing import Dict, Any, List, Optional
from orchestrator.offline.models import SyncConflictStatus, QueuedOfflineAction

class OfflineSyncManager:
    """Manages offline request queueing, synchronization on reconnect, and conflict resolution."""
    def __init__(self):
        self._offline_queue: List[QueuedOfflineAction] = []
        self._server_state: Dict[str, Dict[str, Any]] = {}  # entity_id -> state dict

    def enqueue_action(self, action: QueuedOfflineAction):
        self._offline_queue.append(action)

    def get_queued_actions(self, user_id: str) -> List[QueuedOfflineAction]:
        return [a for a in self._offline_queue if a.user_id == user_id]

    def clear_queue(self, user_id: str):
        self._offline_queue = [a for a in self._offline_queue if a.user_id != user_id]

    @staticmethod
    def detect_conflict(
        local_version: int,
        local_timestamp: str,
        remote_version: int,
        remote_timestamp: str
    ) -> SyncConflictStatus:
        if local_version > remote_version:
            return SyncConflictStatus.LOCAL_NEWER
        elif remote_version > local_version:
            return SyncConflictStatus.REMOTE_NEWER
        elif local_timestamp == remote_timestamp:
            return SyncConflictStatus.MERGED
        return SyncConflictStatus.CONFLICT
