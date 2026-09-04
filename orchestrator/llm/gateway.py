import os
import asyncio
from typing import Dict, List, Optional, Type
from orchestrator.llm.models import LLMGatewayResponse, LLMUsage, LLMRequestRequirement
from orchestrator.llm.provider import (
    BaseLLMProvider,
    AnthropicProvider,
    OpenAIProvider,
    GoogleGeminiProvider,
    HuggingFaceProvider,
    LocalFallbackProvider,
)
from orchestrator.observability import default_metrics, jarvis_logger

class LLMGateway:
    """
    Centralized LLM Gateway providing capability-aware routing, bounded fallbacks,
    token/cost usage tracking, provider health management, and observability metrics.
    """
    def __init__(self):
        self.providers: List[BaseLLMProvider] = []
        self._init_providers_from_env()

    def _init_providers_from_env(self) -> None:
        claude_key = os.getenv("CLAUDE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        hf_key = os.getenv("HF_API_KEY")

        if claude_key:
            self.providers.append(AnthropicProvider(api_key=claude_key))
        if openai_key:
            self.providers.append(OpenAIProvider(api_key=openai_key))
        if gemini_key:
            self.providers.append(GoogleGeminiProvider(api_key=gemini_key))
        if hf_key:
            self.providers.append(HuggingFaceProvider(api_key=hf_key))

        # Always append local fallback provider as guaranteed safety net
        self.providers.append(LocalFallbackProvider())

    def register_provider(self, provider: BaseLLMProvider) -> None:
        self.providers.insert(0, provider)

    def select_provider(self, requirement: Optional[LLMRequestRequirement] = None) -> BaseLLMProvider:
        req = requirement or LLMRequestRequirement()
        healthy_providers = [p for p in self.providers if p.check_health()]

        if not healthy_providers:
            return LocalFallbackProvider()

        # Capability / Task routing
        if req.task_type in {"coding", "reasoning"}:
            for p in healthy_providers:
                if any(cap in p.capabilities for cap in ["coding", "reasoning"]):
                    return p

        if req.preferred_speed == "fast":
            for p in healthy_providers:
                if "speed" in p.capabilities:
                    return p

        return healthy_providers[0]

    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        requirement: Optional[LLMRequestRequirement] = None,
        max_retries: int = 2,
    ) -> LLMGatewayResponse:
        primary = self.select_provider(requirement)
        providers_to_try = [primary] + [p for p in self.providers if p != primary and p.check_health()]

        is_fallback = False
        last_exception = None

        for idx, provider in enumerate(providers_to_try):
            if idx > 0:
                is_fallback = True

            for attempt in range(1, max_retries + 1):
                try:
                    res = await provider.generate(messages=messages, system_prompt=system_prompt)
                    res.is_fallback = is_fallback
                    provider.consecutive_failures = 0

                    default_metrics.record_llm(
                        model=res.model_name,
                        duration_ms=res.usage.latency_ms,
                        success=True,
                        is_fallback=is_fallback,
                    )
                    return res
                except Exception as exc:
                    provider.consecutive_failures += 1
                    last_exception = exc
                    jarvis_logger.warning(
                        "LLM Gateway provider '%s' (model: %s) attempt %d failed: %s",
                        provider.name, provider.model_name, attempt, exc
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(0.3 * (2 ** (attempt - 1)))

        # Absolute safety net fallback
        fallback = LocalFallbackProvider()
        res = await fallback.generate(messages=messages, system_prompt=system_prompt)
        res.is_fallback = True
        default_metrics.record_llm(model="local_fallback", duration_ms=res.usage.latency_ms, success=True, is_fallback=True)
        return res

default_llm_gateway = LLMGateway()
