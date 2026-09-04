"""
Phase 54: Offline & Edge Capability Models.
"""

import enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class PrivacyMode(str, enum.Enum):
    ONLINE_ONLY = "ONLINE_ONLY"
    LOCAL_PREFERRED = "LOCAL_PREFERRED"
    LOCAL_ONLY = "LOCAL_ONLY"

class NetworkStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    SYNCING = "SYNCING"
    SYNC_ERROR = "SYNC_ERROR"

class SyncConflictStatus(str, enum.Enum):
    LOCAL_NEWER = "LOCAL_NEWER"
    REMOTE_NEWER = "REMOTE_NEWER"
    CONFLICT = "CONFLICT"
    MERGED = "MERGED"

class CapabilityDescriptor(BaseModel):
    name: str
    available_online: bool = True
    available_offline: bool = False
    requires_cloud: bool = False
    requires_local_model: bool = False

class QueuedOfflineAction(BaseModel):
    action_id: str
    user_id: str
    capability_name: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp_iso: str
    client_version: int = 1
