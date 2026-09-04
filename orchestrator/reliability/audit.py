from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from orchestrator.observability import jarvis_logger

class AuditLogger:
    """
    Operational audit logging tracking security events, authorization failures,
    approval resolutions, and workspace permission changes without logging secrets.
    """
    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def log_event(
        self,
        event_type: str, # auth, authorization_failure, approval_resolved, workspace_changed, security_alert
        user_id: str,
        summary: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "summary": summary,
            "details": details or {},
        }
        self.events.append(entry)
        jarvis_logger.info("AUDIT_EVENT [%s] user=%s: %s", event_type, user_id, summary)
        return entry

default_audit_logger = AuditLogger()
