import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from orchestrator.llm import default_llm_gateway, LLMRequestRequirement, BaseLLMProvider, AnthropicProvider, HuggingFaceProvider
from orchestrator.observability import jarvis_logger

logger = logging.getLogger(__name__)

class LLMResponse(BaseModel):
    text: str
    model_used: str
    token_count: Optional[int] = None
    latency_ms: float

class LLMClient:
    """
    Unified LLM client wrapping LLMGateway for backward-compatible call delegation.
    Instrumented with production metrics, provider fallback, and token/cost tracking.
    """
    def __init__(self, claude_api_key: Optional[str] = None, hf_api_key: Optional[str] = None):
        self.claude_api_key = claude_api_key
        self.hf_api_key = hf_api_key

        if claude_api_key and not claude_api_key.startswith("YOUR_"):
            default_llm_gateway.register_provider(AnthropicProvider(api_key=claude_api_key))
        if hf_api_key and not hf_api_key.startswith("YOUR_"):
            default_llm_gateway.register_provider(HuggingFaceProvider(api_key=hf_api_key))

    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model_name: str = "claude-3-5-sonnet-20241022",
        requirement: Optional[LLMRequestRequirement] = None,
    ) -> LLMResponse:
        req = requirement or LLMRequestRequirement(task_type="chat")
        gw_res = await default_llm_gateway.generate(messages=messages, system_prompt=system_prompt, requirement=req)

        return LLMResponse(
            text=gw_res.text,
            model_used=gw_res.model_name,
            token_count=gw_res.usage.total_tokens,
            latency_ms=gw_res.usage.latency_ms,
        )
