"""
Unit Tests for Phase 59: JARVIS Analytics & Intelligence.
"""

import pytest
from orchestrator.analytics import (
    default_analytics_collector,
    default_analytics_engine,
)

def test_metrics_collection_and_aggregation():
    user_id = "user_analytics_1"
    ws_id = "ws_analytics_1"

    default_analytics_collector.record_metric(user_id, "request", 1.0, workspace_id=ws_id)
    default_analytics_collector.record_metric(user_id, "latency", 2500.0, workspace_id=ws_id)
    default_analytics_collector.record_metric(user_id, "cost", 15.0, workspace_id=ws_id)

    metrics = default_analytics_collector.get_metrics_by_user(user_id)
    assert len(metrics) == 3

    summary = default_analytics_engine.compute_summary(user_id=user_id)
    assert summary.total_requests == 3
    assert summary.average_latency_ms == 2500.0
    assert summary.total_cost_usd == 15.0
    assert len(summary.bottlenecks) == 1

    recs = default_analytics_engine.generate_recommendations(user_id=user_id)
    assert len(recs) == 2
