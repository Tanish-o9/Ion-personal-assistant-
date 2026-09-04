import os
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

SENSITIVE_KEYS = {"password", "token", "authorization", "api_key", "secret", "password_hash"}

def sanitize_data(data: Any) -> Any:
    """
    Recursively redacts sensitive keys from dictionaries before logging.
    """
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if k.lower() in SENSITIVE_KEYS:
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = sanitize_data(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    return data

class StructuredJsonFormatter(logging.Formatter):
    """
    Formats log records as structured JSON string.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "jarvis-orchestrator",
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add custom extra context attributes if provided
        for attr in ("request_id", "user_id", "session_id", "job_id", "duration_ms", "event", "error"):
            if hasattr(record, attr):
                val = getattr(record, attr)
                log_obj[attr] = sanitize_data(val)

        if record.exc_info:
            log_obj["error"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)

def setup_logging(level_name: Optional[str] = None) -> logging.Logger:
    """
    Configures centralized structured logging for JARVIS.
    """
    log_level = level_name or os.getenv("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger("jarvis")
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)

    return logger

jarvis_logger = setup_logging()
