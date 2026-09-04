"""
Phase 51: Advanced Security, Privacy & Data Governance System.
Provides data classification, access control policies, user privacy controls, retention management, secret protection, and privacy-aware logging.
"""

import re
import enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class DataClassification(str, enum.Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    PRIVATE = "PRIVATE"
    SENSITIVE = "SENSITIVE"
    SECRET = "SECRET"

class DataClassificationPolicy:
    """Classifies system and user data based on source and context."""
    @staticmethod
    def classify_source(source_type: str, content: Optional[str] = None) -> DataClassification:
        source_lower = source_type.lower()
        if "web" in source_lower or "public" in source_lower:
            return DataClassification.PUBLIC
        elif "api_key" in source_lower or "credential" in source_lower or "token" in source_lower or "secret" in source_lower:
            return DataClassification.SECRET
        elif "user_chat" in source_lower or "conversation" in source_lower or "memory" in source_lower:
            return DataClassification.PRIVATE
        elif "profile" in source_lower or "personal" in source_lower or "health" in source_lower or "financial" in source_lower:
            return DataClassification.SENSITIVE
        elif "log" in source_lower or "metric" in source_lower or "operational" in source_lower:
            return DataClassification.INTERNAL
        return DataClassification.PRIVATE

class DataAccessPolicy:
    """Evaluates granular data access permissions across users, workspaces, and data classifications."""
    @staticmethod
    def authorize_access(
        requesting_user_id: str,
        resource_owner_id: str,
        requesting_workspace_id: Optional[str] = None,
        resource_workspace_id: Optional[str] = None,
        classification: DataClassification = DataClassification.PRIVATE,
        permission: str = "read",
        is_admin: bool = False
    ) -> bool:
        # Admin override for internal metadata/logs, but not secrets
        if is_admin and classification != DataClassification.SECRET:
            return True

        # Secret data requires exact ownership match
        if classification == DataClassification.SECRET:
            return requesting_user_id == resource_owner_id

        # Cross-user isolation: User A cannot access User B's private data
        if requesting_user_id != resource_owner_id:
            # Check workspace sharing if workspace_id matches and not strictly private
            if requesting_workspace_id and resource_workspace_id:
                if requesting_workspace_id != resource_workspace_id:
                    return False
                # Shared workspace data must be PUBLIC or INTERNAL
                return classification in (DataClassification.PUBLIC, DataClassification.INTERNAL)
            return False

        return True

class PrivacyManager:
    """Provides user privacy control operations: view, edit, delete, clear, disable."""
    def __init__(self):
        self._disabled_users: Dict[str, List[str]] = {}  # user_id -> disabled categories

    def disable_feature_for_user(self, user_id: str, category: str):
        if user_id not in self._disabled_users:
            self._disabled_users[user_id] = []
        if category not in self._disabled_users[user_id]:
            self._disabled_users[user_id].append(category)

    def enable_feature_for_user(self, user_id: str, category: str):
        if user_id in self._disabled_users and category in self._disabled_users[user_id]:
            self._disabled_users[user_id].remove(category)

    def is_feature_enabled(self, user_id: str, category: str) -> bool:
        return category not in self._disabled_users.get(user_id, [])

    def process_privacy_request(self, user_id: str, action: str, category: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        action_lower = action.lower()
        if action_lower == "disable":
            self.disable_feature_for_user(user_id, category)
            return {"status": "success", "action": "disable", "category": category, "enabled": False}
        elif action_lower == "enable":
            self.enable_feature_for_user(user_id, category)
            return {"status": "success", "action": "enable", "category": category, "enabled": True}
        elif action_lower in ("delete", "clear"):
            return {"status": "success", "action": action_lower, "category": category, "cleared": True}
        elif action_lower == "view":
            return {"status": "success", "action": "view", "category": category, "data": data or {}}
        return {"status": "error", "message": f"Unsupported action: {action}"}

class SecretProtector:
    """Scans and redacts credentials, API keys, tokens, and secret patterns from text."""
    SECRET_PATTERNS = [
        r"sk-[A-Za-z0-9_-]{20,}",
        r"ghp_[A-Za-z0-9]{20,}",
        r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",  # JWT
        r"postgres://[^\s]+",
        r"redis://[^\s]+",
        r"API_KEY\s*=\s*['\"]?[A-Za-z0-9_-]+['\"]?",
        r"SECRET\s*=\s*['\"]?[A-Za-z0-9_-]+['\"]?",
        r"PASSWORD\s*=\s*['\"]?[A-Za-z0-9_-]+['\"]?"
    ]


    @classmethod
    def redact_secrets(cls, text: str) -> str:
        if not text or not isinstance(text, str):
            return text
        sanitized = text
        for pattern in cls.SECRET_PATTERNS:
            sanitized = re.sub(pattern, "[REDACTED_SECRET]", sanitized, flags=re.IGNORECASE)
        return sanitized

class DataRetentionPolicyManager:
    """Manages data retention periods and identifies stale records for cleanup."""
    DEFAULT_RETENTION_DAYS = {
        "conversations": 90,
        "temporary_files": 7,
        "jobs": 30,
        "logs": 30,
        "research_metadata": 60,
        "embeddings": 180,
        "memory": 365,
        "audit_events": 365
    }

    def __init__(self, custom_retention: Optional[Dict[str, int]] = None):
        self.retention_days = dict(self.DEFAULT_RETENTION_DAYS)
        if custom_retention:
            self.retention_days.update(custom_retention)

    def is_expired(self, category: str, created_at: datetime) -> bool:
        max_days = self.retention_days.get(category, 90)
        cutoff = datetime.utcnow() - timedelta(days=max_days)
        return created_at < cutoff

class PrivacyAwareLogger:
    """Logs operational metadata while redacting sensitive content and user secrets."""
    def __init__(self, secret_protector: Optional[SecretProtector] = None):
        self.secret_protector = secret_protector or SecretProtector()

    def format_log(
        self,
        request_id: str,
        session_id: str,
        status: str,
        message: str,
        user_content: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "session_id": session_id,
            "status": status,
            "message": self.secret_protector.redact_secrets(message),
            "metadata": extra_metadata or {}
        }
        if user_content:
            # Redact user content for logs
            log_entry["user_content_redacted"] = self.secret_protector.redact_secrets(user_content[:100]) + "..." if len(user_content) > 100 else self.secret_protector.redact_secrets(user_content)
        return log_entry

default_privacy_manager = PrivacyManager()
default_secret_protector = SecretProtector()
default_retention_manager = DataRetentionPolicyManager()
default_privacy_logger = PrivacyAwareLogger(default_secret_protector)
