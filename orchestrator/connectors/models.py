"""
Phase 57: Connector Models & Permission Enums.
"""

import enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class PermissionScope(str, enum.Enum):
    READ = "READ"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SEND = "SEND"
    SHARE = "SHARE"

class ConnectorDescriptor(BaseModel):
    connector_id: str
    name: str
    provider: str
    version: str = "1.0.0"
    capabilities: List[str] = Field(default_factory=list)
    required_scopes: List[PermissionScope] = Field(default_factory=list)
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH
    is_enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
