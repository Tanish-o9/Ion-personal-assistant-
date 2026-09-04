"""
Phase 89: Device Security, Permissions & Safety Layer.
Enforces permission checks, conservative risk classification, approval integration, secret redaction, and audit logging.
"""

import json
import re
import uuid
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from orchestrator.devices.models import DeviceCapability, DeviceDetail
from orchestrator.approval.manager import default_approval_manager
from database.connection import get_db_context
from database.models import DeviceAuditEventModel, utc_now_iso

# Secret redaction patterns
SECRET_PATTERNS = [
    re.compile(r"(?i)(api_key|token|password|secret|auth|bearer)\s*[:=]\s*['\"]?([^\s'\"}{]+)['\"]?"),
]

class DeviceSecurityPolicy:
    """Security policy guard for permission verification, risk classification, secret redaction, and audit logging."""

    @staticmethod
    def redact_secrets(data: Any) -> Any:
        """Redacts raw credentials and private tokens from strings, dicts, or lists."""
        if isinstance(data, str):
            res = data
            for pattern in SECRET_PATTERNS:
                res = pattern.sub(r"\1: [REDACTED]", res)
            return res
        elif isinstance(data, dict):
            redacted = {}
            for k, v in data.items():
                if any(secret_kw in k.lower() for secret_kw in ("password", "secret", "token", "api_key", "credential", "bearer")):
                    redacted[k] = "[REDACTED]"
                else:
                    redacted[k] = DeviceSecurityPolicy.redact_secrets(v)
            return redacted
        elif isinstance(data, list):
            return [DeviceSecurityPolicy.redact_secrets(item) for item in data]
        return data

    @staticmethod
    def classify_action_risk(capability: DeviceCapability, parameters: Dict[str, Any]) -> str:
        """Classifies action into LOW, MEDIUM, HIGH, or BLOCKED."""
        cap_val = capability.value

        # BLOCKED: dangerous physical actions or credential extraction
        if "weapon" in str(parameters).lower() or "bypass" in str(parameters).lower():
            return "BLOCKED"

        # HIGH risk: consequential state changes e.g. main power shutdown or thermal override
        if cap_val == "SET_STATE" and parameters.get("power") == "OFF" and parameters.get("scope") == "CRITICAL":
            return "HIGH"
        if cap_val == "SET_TEMPERATURE" and (parameters.get("temperature", 20.0) > 40.0 or parameters.get("temperature", 20.0) < 5.0):
            return "HIGH"

        # MEDIUM risk: general state changes, brightness, display message
        if cap_val in ("SET_STATE", "SET_BRIGHTNESS", "SET_TEMPERATURE", "DISPLAY_MESSAGE", "PLAY_MEDIA"):
            return "MEDIUM"

        # LOW risk: read-only status and sensor queries
        return "LOW"

    def authorize_and_audit(
        self,
        user_id: str,
        device: DeviceDetail,
        capability: DeviceCapability,
        parameters: Dict[str, Any],
        workspace_id: Optional[str] = None
    ) -> Tuple[bool, str, bool, Optional[str]]:
        """
        Executes complete security pipeline:
        Auth Check -> Workspace Isolation -> Capability Validation -> Risk Policy -> Approval Trigger -> Audit Event.
        Returns: (is_authorized, risk_level, approval_required, approval_id)
        """
        # Tenant & Workspace check
        if device.user_id != user_id:
            self._log_audit_event(user_id, workspace_id, device.id, capability.value, "BLOCKED", "UNAUTHORIZED_USER", "REJECTED")
            return False, "BLOCKED", False, None

        if workspace_id and device.workspace_id and device.workspace_id != workspace_id:
            self._log_audit_event(user_id, workspace_id, device.id, capability.value, "BLOCKED", "WORKSPACE_MISMATCH", "REJECTED")
            return False, "BLOCKED", False, None

        # Risk classification
        risk_level = self.classify_action_risk(capability, parameters)
        if risk_level == "BLOCKED":
            self._log_audit_event(user_id, workspace_id, device.id, capability.value, "BLOCKED", "POLICY_BLOCKED", "REJECTED")
            return False, "BLOCKED", False, None

        # HIGH risk triggers Phase 26 Approval
        if risk_level == "HIGH":
            approval = default_approval_manager.create_approval(
                user_id=user_id,
                session_id=device.id,
                action_type=f"device_action:{capability.value}",
                action_summary=f"Execute high-risk action {capability.value} on device {device.name}",
                risk_level="high"
            )
            appr_id = approval.get("id", f"appr_{uuid.uuid4().hex[:12]}")
            self._log_audit_event(user_id, workspace_id, device.id, capability.value, "HIGH", "PENDING_APPROVAL", "WAITING")
            return False, "HIGH", True, appr_id


        self._log_audit_event(user_id, workspace_id, device.id, capability.value, risk_level, "NOT_REQUIRED", "COMPLETED")
        return True, risk_level, False, None

    def _log_audit_event(
        self,
        user_id: str,
        workspace_id: Optional[str],
        device_id: str,
        action: str,
        risk_level: str,
        approval_status: str,
        status: str
    ) -> None:
        try:
            with get_db_context() as db:
                event = DeviceAuditEventModel(
                    id=f"devaudit_{uuid.uuid4().hex[:12]}",
                    user_id=user_id,
                    workspace_id=workspace_id,
                    device_id=device_id,
                    action=action,
                    risk_level=risk_level,
                    approval_status=approval_status,
                    status=status,
                    created_at=utc_now_iso()
                )
                db.add(event)
                db.commit()
        except Exception:
            pass

default_device_security_policy = DeviceSecurityPolicy()
