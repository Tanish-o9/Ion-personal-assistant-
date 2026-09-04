from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ResourceLimits(BaseModel):
    max_llm_calls: int = 50
    max_tokens: int = 100000
    max_tool_calls: int = 20
    max_web_requests: int = 30
    max_job_runtime_sec: float = 3600.0

class ResourceUsage(BaseModel):
    llm_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    tool_calls: int = 0
    web_requests: int = 0
    estimated_cost_usd: float = 0.0

class BudgetStatus(BaseModel):
    within_budget: bool = True
    warning_issued: bool = False
    limit_exceeded: bool = False
    action: str = "allow" # allow, soft_warning, hard_limit_block
    message: Optional[str] = None
