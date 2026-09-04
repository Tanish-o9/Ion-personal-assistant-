from typing import Dict, Optional
from orchestrator.resources.models import ResourceLimits, ResourceUsage, BudgetStatus
from orchestrator.observability import jarvis_logger

MODEL_PRICING_PER_1K_TOKENS = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
    "default": {"input": 0.001, "output": 0.002},
}

class ResourceManager:
    """
    Centralized resource manager tracking tokens, LLM calls, tools, costs, and enforcing budget limits.
    """
    def __init__(self, default_limits: Optional[ResourceLimits] = None):
        self.default_limits = default_limits or ResourceLimits()
        self.user_usage: Dict[str, ResourceUsage] = {}

    def get_user_usage(self, user_id: str) -> ResourceUsage:
        if user_id not in self.user_usage:
            self.user_usage[user_id] = ResourceUsage()
        return self.user_usage[user_id]

    def record_usage(
        self,
        user_id: str,
        model_name: str = "default",
        input_tokens: int = 0,
        output_tokens: int = 0,
        tool_calls: int = 0,
        web_requests: int = 0,
    ) -> ResourceUsage:
        usage = self.get_user_usage(user_id)
        usage.llm_calls += 1 if (input_tokens > 0 or output_tokens > 0) else 0
        usage.input_tokens += input_tokens
        usage.output_tokens += output_tokens
        usage.total_tokens = usage.input_tokens + usage.output_tokens
        usage.tool_calls += tool_calls
        usage.web_requests += web_requests

        # Cost calculation
        pricing = MODEL_PRICING_PER_1K_TOKENS.get(model_name, MODEL_PRICING_PER_1K_TOKENS["default"])
        cost = (input_tokens / 1000.0 * pricing["input"]) + (output_tokens / 1000.0 * pricing["output"])
        usage.estimated_cost_usd += round(cost, 6)

        return usage

    def check_budget(self, user_id: str, limits: Optional[ResourceLimits] = None) -> BudgetStatus:
        lim = limits or self.default_limits
        usage = self.get_user_usage(user_id)

        # Hard limit check
        if usage.total_tokens >= lim.max_tokens or usage.llm_calls >= lim.max_llm_calls:
            return BudgetStatus(
                within_budget=False,
                limit_exceeded=True,
                action="hard_limit_block",
                message=f"Hard resource limit exceeded: {usage.total_tokens}/{lim.max_tokens} tokens used.",
            )

        # Soft warning check (80% threshold)
        if usage.total_tokens >= (lim.max_tokens * 0.8) or usage.llm_calls >= (lim.max_llm_calls * 0.8):
            return BudgetStatus(
                within_budget=True,
                warning_issued=True,
                action="soft_warning",
                message=f"Soft warning: 80%+ of resource budget consumed ({usage.total_tokens}/{lim.max_tokens} tokens).",
            )

        return BudgetStatus(within_budget=True, action="allow")

default_resource_manager = ResourceManager()
