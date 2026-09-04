from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class AutomationCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    workflow_text: str
    schedule_cron: str = "0 9 * * 1"
    timezone: str = "UTC"
    requires_approval: bool = False

class AutomationResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    workflow_text: str
    schedule_cron: str
    timezone: str
    enabled: bool
    next_run_at: Optional[str] = None
    last_run_at: Optional[str] = None
    created_at: str
