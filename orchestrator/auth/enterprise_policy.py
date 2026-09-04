from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

class EnterpriseRole(str, Enum):
    ORG_OWNER = "ORG_OWNER"
    ORG_ADMIN = "ORG_ADMIN"
    WORKSPACE_ADMIN = "WORKSPACE_ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"

ROLE_PERMISSIONS: Dict[EnterpriseRole, List[str]] = {
    EnterpriseRole.ORG_OWNER: ["*"],
    EnterpriseRole.ORG_ADMIN: ["org:manage", "workspace:create", "workspace:manage", "policy:write", "budget:manage", "audit:read"],
    EnterpriseRole.WORKSPACE_ADMIN: ["workspace:manage", "project:create", "policy:read", "budget:read", "audit:read"],
    EnterpriseRole.MEMBER: ["project:read", "project:write", "tool:execute", "chat:execute"],
    EnterpriseRole.VIEWER: ["project:read", "audit:read"],
}

@dataclass
class EnterprisePolicy:
    organization_id: str
    workspace_id: Optional[str] = None
    allowed_models: List[str] = field(default_factory=lambda: ["gpt-4o", "claude-3-5-sonnet", "jarvis-v5"])
    allowed_providers: List[str] = field(default_factory=lambda: ["openai", "anthropic", "local"])
    allowed_connectors: List[str] = field(default_factory=lambda: ["slack", "github", "jira", "google_drive"])
    allowed_capabilities: List[str] = field(default_factory=lambda: ["*"])
    max_monthly_budget_usd: float = 5000.0
    data_residency_region: str = "us-east-1"
    retention_days: int = 90
    approval_required_for_high_risk: bool = True

class EnterprisePolicyManager:
    def __init__(self):
        self._policies: Dict[str, EnterprisePolicy] = {}

    def set_policy(self, policy: EnterprisePolicy):
        key = f"{policy.organization_id}:{policy.workspace_id or 'GLOBAL'}"
        self._policies[key] = policy

    def get_effective_policy(self, organization_id: str, workspace_id: Optional[str] = None) -> EnterprisePolicy:
        # Check workspace policy first
        if workspace_id:
            ws_key = f"{organization_id}:{workspace_id}"
            if ws_key in self._policies:
                return self._policies[ws_key]

        # Check org global policy
        org_key = f"{organization_id}:GLOBAL"
        if org_key in self._policies:
            return self._policies[org_key]

        # Default fallback policy
        return EnterprisePolicy(organization_id=organization_id, workspace_id=workspace_id)

    def validate_capability_access(
        self,
        organization_id: str,
        workspace_id: Optional[str],
        capability_name: str,
        model_name: Optional[str] = None,
    ) -> bool:
        policy = self.get_effective_policy(organization_id, workspace_id)
        if policy.allowed_capabilities != ["*"] and capability_name not in policy.allowed_capabilities:
            return False
        if model_name and policy.allowed_models != ["*"] and model_name not in policy.allowed_models:
            return False
        return True

class MultiTierBudgetManager:
    def __init__(self, policy_manager: EnterprisePolicyManager):
        self.policy_manager = policy_manager
        self._spent: Dict[str, float] = {}

    def record_usage(self, entity_id: str, cost_usd: float):
        self._spent[entity_id] = self._spent.get(entity_id, 0.0) + cost_usd

    def validate_budget(
        self,
        organization_id: str,
        workspace_id: Optional[str],
        requested_cost_usd: float,
    ) -> bool:
        policy = self.policy_manager.get_effective_policy(organization_id, workspace_id)
        current_spent = self._spent.get(organization_id, 0.0)
        if current_spent + requested_cost_usd > policy.max_monthly_budget_usd:
            raise PermissionError(f"Enterprise budget limit exceeded: ${current_spent + requested_cost_usd:.2f} > ${policy.max_monthly_budget_usd:.2f}")
        return True

class EnterpriseResourceOwnershipManager:
    def validate_resource_access(
        self,
        user_role: EnterpriseRole,
        resource_org_id: str,
        resource_workspace_id: Optional[str],
        user_org_id: str,
        user_workspace_id: Optional[str],
    ) -> bool:
        # Cross-tenant restriction
        if resource_org_id != user_org_id:
            raise PermissionError("Cross-tenant organization access forbidden")

        if resource_workspace_id and user_workspace_id and resource_workspace_id != user_workspace_id:
            if user_role not in [EnterpriseRole.ORG_OWNER, EnterpriseRole.ORG_ADMIN]:
                raise PermissionError("Cross-tenant workspace access forbidden for role " + user_role.value)

        return True

class EnterpriseAuditLogger:
    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def log_event(
        self,
        organization_id: str,
        workspace_id: Optional[str],
        user_id: str,
        event_type: str,
        resource_type: str,
        resource_id: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.events.append({
            "id": str(uuid.uuid4()),
            "organization_id": organization_id,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "event_type": event_type,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "metadata": metadata or {},
        })
