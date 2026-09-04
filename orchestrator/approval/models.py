from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ApprovalRequestPayload(BaseModel):
    session_id: str
    action_type: str
    action_summary: str
    risk_level: str = "medium"
    job_id: Optional[str] = None
    expires_in_seconds: int = 3600

class ApprovalResponse(BaseModel):
    id: str
    user_id: str
    session_id: str
    job_id: Optional[str] = None
    action_type: str
    action_summary: str
    risk_level: str
    status: str
    created_at: str
    expires_at: str
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None
