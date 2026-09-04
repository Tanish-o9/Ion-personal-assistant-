"""
Phase 59: Analytics & Intelligence Models.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class AnalyticsMetric(BaseModel):
    user_id: str
    workspace_id: Optional[str] = None
    metric_type: str  # request, llm_tokens, tool_execution, goal_completion, error
    value: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp_iso: Optional[str] = None

class SystemPerformanceSummary(BaseModel):
    total_requests: int = 0
    success_rate: float = 1.0
    average_latency_ms: float = 0.0
    total_cost_usd: float = 0.0
    most_used_tools: List[str] = Field(default_factory=list)
    bottlenecks: List[str] = Field(default_factory=list)

class OptimizationRecommendation(BaseModel):
    category: str  # cost, latency, reliability, model
    suggestion: str
    impact: str  # HIGH, MEDIUM, LOW
    action_item: str
