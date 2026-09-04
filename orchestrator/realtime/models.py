"""
Phase 52: Real-Time Intelligence Models & Enums.
"""

import enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ChangeStatus(str, enum.Enum):
    NEW = "NEW"
    UPDATED = "UPDATED"
    UNCHANGED = "UNCHANGED"
    REMOVED = "REMOVED"
    CONFLICTING = "CONFLICTING"

class InformationSource(BaseModel):
    source_id: str
    source_type: str  # e.g., "web", "api", "rss"
    name: str
    url: Optional[str] = None
    freshness_ttl_seconds: int = 3600
    last_fetched_at: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class InformationUpdate(BaseModel):
    update_id: str
    source_id: str
    title: str
    snippet: str
    url: Optional[str] = None
    content_hash: str
    status: ChangeStatus = ChangeStatus.NEW
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Subscription(BaseModel):
    subscription_id: str
    user_id: str
    workspace_id: Optional[str] = None
    topic: str
    source_ids: List[str] = Field(default_factory=list)
    frequency_seconds: int = 3600
    freshness_threshold_seconds: int = 7200
    notification_preference: str = "in_app"
    is_active: bool = True
    last_evaluated_at: Optional[str] = None
