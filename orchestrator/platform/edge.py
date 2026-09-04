"""
Phase 88: JARVIS Edge & Local Intelligence Engine.
Capability-aware routing between Local, Remote, and Hybrid execution paths with strict Privacy Mode enforcement.
"""

import enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class EdgeCapability(str, enum.Enum):
    LOCAL_LLM = "LOCAL_LLM"
    LOCAL_EMBEDDING = "LOCAL_EMBEDDING"
    LOCAL_STT = "LOCAL_STT"
    LOCAL_TTS = "LOCAL_TTS"
    LOCAL_CLASSIFICATION = "LOCAL_CLASSIFICATION"
    LOCAL_CACHE = "LOCAL_CACHE"

class PrivacyMode(str, enum.Enum):
    DEFAULT = "DEFAULT"
    LOCAL_ONLY = "LOCAL_ONLY"
    REMOTE_ALLOWED = "REMOTE_ALLOWED"
    HYBRID = "HYBRID"

class ExecutionTarget(str, enum.Enum):
    LOCAL = "LOCAL"
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    BLOCKED = "BLOCKED"

class EdgeRouteDecision(BaseModel):
    task_type: str
    target: ExecutionTarget
    selected_model: str
    privacy_mode: PrivacyMode
    reason: str
    latency_estimate_ms: float = 50.0
    cost_estimate_usd: float = 0.0

class EdgeRuntime:
    """Manages local edge capabilities, health signals, resource limits, and privacy routing."""

    def __init__(self):
        self._capabilities: Dict[EdgeCapability, str] = {
            EdgeCapability.LOCAL_CLASSIFICATION: "rule_classifier_v1",
            EdgeCapability.LOCAL_CACHE: "redis_lru_v1"
        }
        self._resource_limits = {"max_cpu_percent": 80.0, "max_ram_mb": 2048.0}
        self._is_online = True

    def register_capability(self, capability: EdgeCapability, model_name: str) -> None:
        self._capabilities[capability] = model_name

    def remove_capability(self, capability: EdgeCapability) -> None:
        self._capabilities.pop(capability, None)

    def set_connectivity(self, is_online: bool) -> None:
        self._is_online = is_online

    def get_health(self) -> Dict[str, Any]:
        return {
            "online": self._is_online,
            "capabilities": [c.value for c in self._capabilities.keys()],
            "resource_limits": self._resource_limits
        }

    def route_request(
        self,
        task_type: str,
        privacy_mode: PrivacyMode = PrivacyMode.DEFAULT,
        content: str = "",
        max_cost_budget: float = 1.0
    ) -> EdgeRouteDecision:
        """Determines whether task runs LOCAL, REMOTE, or HYBRID with strict privacy guarantees."""

        # 1. Check LOCAL_ONLY Privacy Mode
        if privacy_mode == PrivacyMode.LOCAL_ONLY:
            # Must check if matching local capability exists
            if task_type in ("classification", "cache") and EdgeCapability.LOCAL_CLASSIFICATION in self._capabilities:
                return EdgeRouteDecision(
                    task_type=task_type,
                    target=ExecutionTarget.LOCAL,
                    selected_model=self._capabilities[EdgeCapability.LOCAL_CLASSIFICATION],
                    privacy_mode=privacy_mode,
                    reason="LOCAL_ONLY mode enforced; satisfied by local classification model.",
                    cost_estimate_usd=0.0
                )
            elif task_type == "llm" and EdgeCapability.LOCAL_LLM in self._capabilities:
                return EdgeRouteDecision(
                    task_type=task_type,
                    target=ExecutionTarget.LOCAL,
                    selected_model=self._capabilities[EdgeCapability.LOCAL_LLM],
                    privacy_mode=privacy_mode,
                    reason="LOCAL_ONLY mode enforced; satisfied by local LLM.",
                    cost_estimate_usd=0.0
                )
            else:
                # Strictly block remote fallback when LOCAL_ONLY mode is active and local capability missing
                return EdgeRouteDecision(
                    task_type=task_type,
                    target=ExecutionTarget.BLOCKED,
                    selected_model="NONE",
                    privacy_mode=privacy_mode,
                    reason=f"LOCAL_ONLY mode active but required local capability '{task_type}' is unavailable. Remote fallback prohibited.",
                    cost_estimate_usd=0.0
                )

        # 2. Check Offline Connectivity
        if not self._is_online:
            if EdgeCapability.LOCAL_LLM in self._capabilities or task_type in ("classification", "cache"):
                return EdgeRouteDecision(
                    task_type=task_type,
                    target=ExecutionTarget.LOCAL,
                    selected_model=self._capabilities.get(EdgeCapability.LOCAL_LLM, "local_fallback"),
                    privacy_mode=privacy_mode,
                    reason="Network offline; routed to local edge runtime.",
                    cost_estimate_usd=0.0
                )
            return EdgeRouteDecision(
                task_type=task_type,
                target=ExecutionTarget.BLOCKED,
                selected_model="NONE",
                privacy_mode=privacy_mode,
                reason="Network offline and no local capability available.",
                cost_estimate_usd=0.0
            )

        # 3. Default / Hybrid Routing based on cost and task complexity
        if task_type in ("classification", "lightweight") and EdgeCapability.LOCAL_CLASSIFICATION in self._capabilities:
            return EdgeRouteDecision(
                task_type=task_type,
                target=ExecutionTarget.LOCAL,
                selected_model=self._capabilities[EdgeCapability.LOCAL_CLASSIFICATION],
                privacy_mode=privacy_mode,
                reason="Simple task routed locally for minimum latency and zero cost.",
                cost_estimate_usd=0.0
            )

        return EdgeRouteDecision(
            task_type=task_type,
            target=ExecutionTarget.REMOTE,
            selected_model="claude-3-5-sonnet-20241022",
            privacy_mode=privacy_mode,
            reason="Complex task routed to primary cloud LLM provider.",
            cost_estimate_usd=0.01
        )

default_edge_runtime = EdgeRuntime()
