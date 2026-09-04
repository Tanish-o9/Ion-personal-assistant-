import time
import uuid
import contextvars
from typing import Optional

request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_id", default=None)
user_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("user_id", default=None)
session_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("session_id", default=None)

def generate_request_id() -> str:
    """
    Generates a unique tracing request ID formatted as req_uuid.
    """
    return f"req_{uuid.uuid4().hex[:12]}"

def set_trace_context(request_id: str, user_id: Optional[str] = None, session_id: Optional[str] = None) -> None:
    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if session_id:
        session_id_var.set(session_id)

def get_current_request_id() -> Optional[str]:
    return request_id_var.get()
