from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class EvaluationCase(BaseModel):
    case_id: str
    category: str # chat, tool_use, planning, research, rag, multimodal, coding, document, security
    input_prompt: str
    expected_tool: Optional[str] = None
    expected_keywords: List[str] = Field(default_factory=list)
    max_latency_ms: float = 5000.0

class EvaluationResult(BaseModel):
    case_id: str
    category: str
    passed: bool
    actual_output: str
    actual_tool_used: Optional[str] = None
    latency_ms: float = 0.0
    tokens_used: int = 0
    failure_reason: Optional[str] = None

class EvaluationRun(BaseModel):
    run_id: str
    timestamp: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate_pct: float
    avg_latency_ms: float
    results: List[EvaluationResult] = Field(default_factory=list)
