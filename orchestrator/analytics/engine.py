"""
Phase 59: Analytics Aggregation & Bottleneck Engine.
"""

from typing import Dict, Any, List, Optional
from orchestrator.analytics.models import SystemPerformanceSummary, OptimizationRecommendation
from orchestrator.analytics.collector import default_analytics_collector

class AnalyticsEngine:
    """Aggregates metrics, detects system performance bottlenecks, and provides optimization recommendations."""

    def compute_summary(self, user_id: Optional[str] = None, workspace_id: Optional[str] = None) -> SystemPerformanceSummary:
        metrics = default_analytics_collector.get_all_metrics()
        if user_id:
            metrics = [m for m in metrics if m.user_id == user_id]
        if workspace_id:
            metrics = [m for m in metrics if m.workspace_id == workspace_id]

        if not metrics:
            return SystemPerformanceSummary()

        total_reqs = len(metrics)
        errors = [m for m in metrics if m.metric_type == "error"]
        latencies = [m.value for m in metrics if m.metric_type == "latency"]
        costs = [m.value for m in metrics if m.metric_type == "cost"]

        succ_rate = 1.0 - (len(errors) / total_reqs) if total_reqs > 0 else 1.0
        avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
        total_cost = sum(costs)

        bottlenecks = []
        if avg_lat > 2000.0:
            bottlenecks.append("High average request latency (>2000ms)")
        if succ_rate < 0.9:
            bottlenecks.append("High failure rate (>10% errors)")

        return SystemPerformanceSummary(
            total_requests=total_reqs,
            success_rate=round(succ_rate, 2),
            average_latency_ms=round(avg_lat, 2),
            total_cost_usd=round(total_cost, 4),
            bottlenecks=bottlenecks
        )

    def generate_recommendations(self, user_id: Optional[str] = None) -> List[OptimizationRecommendation]:
        summary = self.compute_summary(user_id=user_id)
        recs = []

        if summary.average_latency_ms > 2000.0:
            recs.append(OptimizationRecommendation(
                category="latency",
                suggestion="Enable caching for repeated web queries and LLM prompts",
                impact="HIGH",
                action_item="Enable Redis caching in LLM gateway settings"
            ))

        if summary.total_cost_usd > 10.0:
            recs.append(OptimizationRecommendation(
                category="cost",
                suggestion="Consider switching routine tasks to a lightweight model",
                impact="MEDIUM",
                action_item="Update model selection strategy to preference local/fast models"
            ))

        return recs

default_analytics_engine = AnalyticsEngine()
