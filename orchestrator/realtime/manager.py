"""
Phase 52: Real-time Subscriptions & Update Pipeline Manager.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from orchestrator.realtime.models import Subscription, InformationSource, InformationUpdate, ChangeStatus
from orchestrator.realtime.freshness import FreshnessPolicy, ChangeDetector

class RealTimeManager:
    """Manages real-time information sources, user subscriptions, deduplication, and notifications."""
    def __init__(self):
        self._sources: Dict[str, InformationSource] = {}
        self._subscriptions: Dict[str, Subscription] = {}
        self._latest_updates: Dict[str, InformationUpdate] = {}  # source_id -> update
        self._sent_notifications: List[Dict[str, Any]] = []

    def register_source(self, name: str, source_type: str, url: Optional[str] = None, ttl_seconds: int = 3600) -> InformationSource:
        source_id = f"src_{uuid.uuid4().hex[:8]}"
        src = InformationSource(
            source_id=source_id,
            source_type=source_type,
            name=name,
            url=url,
            freshness_ttl_seconds=ttl_seconds
        )
        self._sources[source_id] = src
        return src

    def create_subscription(
        self,
        user_id: str,
        topic: str,
        source_ids: List[str],
        workspace_id: Optional[str] = None,
        frequency_seconds: int = 3600
    ) -> Subscription:
        sub_id = f"sub_{uuid.uuid4().hex[:8]}"
        sub = Subscription(
            subscription_id=sub_id,
            user_id=user_id,
            workspace_id=workspace_id,
            topic=topic,
            source_ids=source_ids,
            frequency_seconds=frequency_seconds
        )
        self._subscriptions[sub_id] = sub
        return sub

    def process_incoming_source_data(self, source_id: str, title: str, snippet: str, url: Optional[str] = None) -> Optional[InformationUpdate]:
        if source_id not in self._sources:
            return None

        src = self._sources[source_id]
        src.last_fetched_at = datetime.utcnow().isoformat()

        prev_update = self._latest_updates.get(source_id)
        status = ChangeDetector.evaluate_change(snippet, title, prev_update)

        if status == ChangeStatus.UNCHANGED and prev_update:
            unchanged_update = prev_update.model_copy(update={"status": ChangeStatus.UNCHANGED})
            return unchanged_update

        content_hash = ChangeDetector.compute_content_hash(snippet)

        update = InformationUpdate(
            update_id=f"upd_{uuid.uuid4().hex[:8]}",
            source_id=source_id,
            title=title,
            snippet=snippet,
            url=url or src.url,
            content_hash=content_hash,
            status=status
        )

        self._latest_updates[source_id] = update

        # Trigger notifications for active subscriptions matching this source
        self._notify_subscribers(update)
        return update

    def _notify_subscribers(self, update: InformationUpdate):
        for sub in self._subscriptions.values():
            if not sub.is_active:
                continue
            if update.source_id in sub.source_ids:
                notification = {
                    "user_id": sub.user_id,
                    "subscription_id": sub.subscription_id,
                    "topic": sub.topic,
                    "update_id": update.update_id,
                    "status": update.status.value,
                    "title": update.title,
                    "snippet": update.snippet,
                    "timestamp": datetime.utcnow().isoformat()
                }
                self._sent_notifications.append(notification)

    def get_user_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        return [n for n in self._sent_notifications if n["user_id"] == user_id]

default_realtime_manager = RealTimeManager()
