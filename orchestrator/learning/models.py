from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class LearningRecordCreate(BaseModel):
    session_id: str
    task_type: str
    skill_used: Optional[str] = None
    tools_used: List[str] = Field(default_factory=list)
    outcome: str = "success" # success, partial_success, failed, cancelled
    failure_reason: Optional[str] = None
    latency_ms: float = 0.0
    cost_usd: float = 0.0

class LearningFeedbackPayload(BaseModel):
    record_id: str
    feedback: str # positive, negative
    reason: Optional[str] = None

class ToolPerformanceMetrics(BaseModel):
    tool_name: str
    total_executions: int = 0
    successes: int = 0
    failures: int = 0
    success_rate: float = 1.0
    average_latency_ms: float = 0.0
