from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class LLMUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    latency_ms: float = 0.0

class LLMGatewayResponse(BaseModel):
    text: str
    provider_name: str
    model_name: str
    usage: LLMUsage
    is_fallback: bool = False

class LLMRequestRequirement(BaseModel):
    task_type: str = "chat"            # chat, coding, reasoning, research, vision
    preferred_speed: str = "normal"    # fast, normal, deep
    context_length_needed: int = 4096
