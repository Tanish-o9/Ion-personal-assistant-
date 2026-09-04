"""
Phase 52: Freshness Policy & Change Detection Engine.
"""

import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from orchestrator.realtime.models import ChangeStatus, InformationUpdate

class FreshnessPolicy:
    """Evaluates whether retrieved knowledge is fresh or requires a real-time update."""
    @staticmethod
    def is_stale(fetched_at_iso: Optional[str], ttl_seconds: int = 3600) -> bool:
        if not fetched_at_iso:
            return True
        try:
            fetched_at = datetime.fromisoformat(fetched_at_iso)
            return datetime.utcnow() - fetched_at > timedelta(seconds=ttl_seconds)
        except Exception:
            return True

class ChangeDetector:
    """Detects NEW, UPDATED, UNCHANGED, REMOVED, or CONFLICTING updates."""
    @staticmethod
    def compute_content_hash(text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    @classmethod
    def evaluate_change(
        cls,
        new_content: str,
        new_title: str,
        previous_update: Optional[InformationUpdate] = None
    ) -> ChangeStatus:
        if not previous_update:
            return ChangeStatus.NEW
        
        new_hash = cls.compute_content_hash(new_content)
        if new_hash == previous_update.content_hash:
            return ChangeStatus.UNCHANGED
        
        # Simple heuristic for updated vs conflicting
        if previous_update.title != new_title and "conflict" in new_content.lower():
            return ChangeStatus.CONFLICTING

        return ChangeStatus.UPDATED
