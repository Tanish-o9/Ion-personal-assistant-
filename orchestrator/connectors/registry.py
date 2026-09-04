"""
Phase 57: Connector Registry & Approval Pipeline.
"""

from typing import Dict, Any, List, Optional
from orchestrator.connectors.models import ConnectorDescriptor, PermissionScope
from orchestrator.connectors.base import BaseConnector
from orchestrator.approval import default_approval_manager
from orchestrator.tools import default_registry

class ConnectorRegistry:
    """Manages connector registration, permission validation, approval checks, and tool export."""

    def __init__(self):
        self._connectors: Dict[str, BaseConnector] = {}

    def register_connector(self, connector: BaseConnector):
        cid = connector.descriptor.connector_id
        self._connectors[cid] = connector

    def get_connector(self, connector_id: str) -> Optional[BaseConnector]:
        return self._connectors.get(connector_id)

    def list_connectors(self) -> List[ConnectorDescriptor]:
        return [c.descriptor for c in self._connectors.values()]

    def execute_action(
        self,
        connector_id: str,
        user_id: str,
        action: str,  # read, create, update, delete
        payload: Dict[str, Any],
        resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        connector = self.get_connector(connector_id)
        if not connector:
            return {"status": "error", "message": f"Connector '{connector_id}' not found"}

        if not connector.descriptor.is_enabled:
            return {"status": "error", "message": f"Connector '{connector_id}' is disabled"}

        # High-risk side-effects (create/update/delete) trigger Phase 26 Human-in-the-Loop approval check
        if action.lower() in ("create", "update", "delete") and connector.descriptor.risk_level == "HIGH":
            req = default_approval_manager.create_approval(
                user_id=user_id,
                session_id=f"conn_{connector_id}",
                action_type=f"connector_{action}",
                action_summary=f"Connector {action} on {connector_id}",
                risk_level="high"
            )
            return {
                "status": "WAITING_FOR_APPROVAL",
                "approval_id": req["id"],
                "message": f"Action '{action}' on connector '{connector_id}' requires explicit approval."
            }


        # Execute action
        if action.lower() == "read":
            res = connector.read(resource_id or "", payload)
        elif action.lower() == "create":
            res = connector.create(payload)
        elif action.lower() == "update":
            res = connector.update(resource_id or "", payload)
        elif action.lower() == "delete":
            deleted = connector.delete(resource_id or "")
            res = {"deleted": deleted}
        else:
            return {"status": "error", "message": f"Unsupported connector action: {action}"}

        return {"status": "success", "result": res}

default_connector_registry = ConnectorRegistry()
