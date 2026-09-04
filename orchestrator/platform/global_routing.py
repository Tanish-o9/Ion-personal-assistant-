from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

class ComponentClassification(str, Enum):
    STATELESS = "STATELESS"
    REGION_LOCAL = "REGION_LOCAL"
    SHARED = "SHARED"
    REPLICATED = "REPLICATED"
    EVENTUAL_CONSISTENCY = "EVENTUAL_CONSISTENCY"
    SINGLE_REGION = "SINGLE_REGION"

COMPONENT_AUDIT_MAP: Dict[str, ComponentClassification] = {
    "api_servers": ComponentClassification.STATELESS,
    "postgresql": ComponentClassification.REPLICATED,
    "redis": ComponentClassification.REGION_LOCAL,
    "object_storage": ComponentClassification.EVENTUAL_CONSISTENCY,
    "background_workers": ComponentClassification.REGION_LOCAL,
    "cron_scheduler": ComponentClassification.SINGLE_REGION,
    "websocket_gateway": ComponentClassification.STATELESS,
    "llm_gateway": ComponentClassification.STATELESS,
    "vector_store": ComponentClassification.REPLICATED,
    "connectors": ComponentClassification.STATELESS,
    "observability": ComponentClassification.SHARED,
}

@dataclass
class Region:
    id: str
    name: str
    status: str = "HEALTHY" # HEALTHY, DEGRADED, OFFLINE
    capabilities: List[str] = field(default_factory=lambda: ["llm", "rag", "vision", "voice", "jobs"])
    provider_availability: Dict[str, bool] = field(default_factory=lambda: {"openai": True, "anthropic": True, "local": True})
    data_residency: List[str] = field(default_factory=lambda: ["us-east-1", "us-west-2", "eu-central-1", "ap-southeast-1"])
    health_score: float = 1.0

class RegionRegistry:
    def __init__(self):
        self._regions: Dict[str, Region] = {
            "us-east-1": Region(id="us-east-1", name="US East (N. Virginia)", data_residency=["us-east-1", "GLOBAL"]),
            "us-west-2": Region(id="us-west-2", name="US West (Oregon)", data_residency=["us-west-2", "GLOBAL"]),
            "eu-central-1": Region(id="eu-central-1", name="EU Central (Frankfurt)", data_residency=["eu-central-1", "EU", "GLOBAL"]),
            "ap-southeast-1": Region(id="ap-southeast-1", name="AP Southeast (Singapore)", data_residency=["ap-southeast-1", "APAC", "GLOBAL"]),
        }

    def get_region(self, region_id: str) -> Optional[Region]:
        return self._regions.get(region_id)

    def register_region(self, region: Region):
        self._regions[region.id] = region

    def list_healthy_regions(self) -> List[Region]:
        return [r for r in self._regions.values() if r.status == "HEALTHY"]

default_region_registry = RegionRegistry()

class RegionRouter:
    def __init__(self, registry: RegionRegistry = default_region_registry):
        self.registry = registry

    def select_region(
        self,
        user_region: str,
        workspace_residency_policy: Optional[str] = None,
        required_capability: Optional[str] = None,
        required_provider: Optional[str] = None,
    ) -> str:
        # 1. Enforce Data Residency Policy strictly
        if workspace_residency_policy and workspace_residency_policy != "GLOBAL":
            target = self.registry.get_region(workspace_residency_policy)
            if target and target.status == "HEALTHY":
                if required_capability and required_capability not in target.capabilities:
                    raise ValueError(f"Required capability {required_capability} unavailable in target region {workspace_residency_policy}")
                return target.id
            raise PermissionError(f"Workspace data residency policy restricts execution to region '{workspace_residency_policy}' which is currently unavailable/unsupported")

        # 2. Match User Region if healthy
        user_target = self.registry.get_region(user_region)
        if user_target and user_target.status == "HEALTHY":
            if (not required_capability or required_capability in user_target.capabilities) and \
               (not required_provider or user_target.provider_availability.get(required_provider, False)):
                return user_target.id

        # 3. Fallback to any healthy region
        for r in self.registry.list_healthy_regions():
            if required_capability and required_capability not in r.capabilities:
                continue
            if required_provider and not r.provider_availability.get(required_provider, False):
                continue
            return r.id

        return "us-east-1" # Default fallback

class GlobalLLMRouter:
    def __init__(self, region_router: RegionRouter):
        self.region_router = region_router

    def route_llm_request(
        self,
        model: str,
        user_region: str,
        workspace_policy: Optional[str] = None,
        privacy_mode: str = "DEFAULT",
    ) -> Dict[str, Any]:
        target_region = self.region_router.select_region(
            user_region=user_region,
            workspace_residency_policy=workspace_policy,
            required_capability="llm"
        )
        return {
            "model": model,
            "target_region": target_region,
            "privacy_mode": privacy_mode,
            "latency_ms": 45.0,
            "routed": True,
        }

class GlobalJobRouter:
    def __init__(self, region_router: RegionRouter):
        self.region_router = region_router

    def route_job(
        self,
        job_id: str,
        user_region: str,
        preferred_region: Optional[str] = None,
        allowed_regions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if allowed_regions and user_region not in allowed_regions and preferred_region not in allowed_regions:
            execution_region = allowed_regions[0]
        else:
            execution_region = preferred_region or user_region

        return {
            "job_id": job_id,
            "preferred_region": preferred_region or user_region,
            "allowed_regions": allowed_regions or [execution_region],
            "execution_region": execution_region,
            "status": "QUEUED",
        }

class GlobalSchedulerSafety:
    def __init__(self):
        self._leases: Dict[str, str] = {} # cron_id -> region_id

    def acquire_lease(self, cron_id: str, region_id: str) -> bool:
        if cron_id in self._leases and self._leases[cron_id] != region_id:
            return False # Active lease held by another region
        self._leases[cron_id] = region_id
        return True

    def release_lease(self, cron_id: str, region_id: str):
        if self._leases.get(cron_id) == region_id:
            del self._leases[cron_id]

class WebSocketSessionManager:
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def save_session_state(self, session_id: str, region_id: str, context: Dict[str, Any]):
        self._sessions[session_id] = {
            "region_id": region_id,
            "context": context,
            "timestamp": str(uuid.uuid4()),
        }

    def recover_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._sessions.get(session_id)

class GlobalFailoverEngine:
    def __init__(self, registry: RegionRegistry = default_region_registry):
        self.registry = registry

    def trigger_failover(self, failed_region_id: str, workspace_policy: Optional[str] = None) -> str:
        region = self.registry.get_region(failed_region_id)
        if region:
            region.status = "OFFLINE"

        if workspace_policy and workspace_policy == failed_region_id:
            raise PermissionError(f"Failover blocked: Workspace policy restricts data to region '{failed_region_id}' which is currently offline.")

        healthy = self.registry.list_healthy_regions()
        if healthy:
            return healthy[0].id
        raise RuntimeError("No healthy failover regions available.")
