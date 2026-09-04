"""
Phase 59: Analytics Collector System.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from orchestrator.analytics.models import AnalyticsMetric

class AnalyticsCollector:
    """Collects system, workspace, and user level operational metrics for platform intelligence."""

    def __init__(self):
        self._metrics: List[AnalyticsMetric] = []

    def record_metric(self, user_id: str, metric_type: str, value: float, workspace_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        metric = AnalyticsMetric(
            user_id=user_id,
            workspace_id=workspace_id,
            metric_type=metric_type,
            value=value,
            metadata=metadata or {},
            timestamp_iso=datetime.utcnow().isoformat()
        )
        self._metrics.append(metric)

    def get_metrics_by_user(self, user_id: str) -> List[AnalyticsMetric]:
        return [m for m in self._metrics if m.user_id == user_id]

    def get_metrics_by_workspace(self, workspace_id: str) -> List[AnalyticsMetric]:
        return [m for m in self._metrics if m.workspace_id == workspace_id]

    def get_all_metrics(self) -> List[AnalyticsMetric]:
        return list(self._metrics)

default_analytics_collector = AnalyticsCollector()
