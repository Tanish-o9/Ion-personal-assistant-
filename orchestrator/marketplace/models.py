"""
Phase 61: Marketplace 2.0 Models.
"""

import enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class CapabilityCategory(str, enum.Enum):
    TOOL = "TOOL"
    SKILL = "SKILL"
    PLUGIN = "PLUGIN"
    AGENT = "AGENT"
    CONNECTOR = "CONNECTOR"
    WORKFLOW_TEMPLATE = "WORKFLOW_TEMPLATE"

class MarketplaceCapabilityEntry(BaseModel):
    id: str
    name: str
    description: str
    publisher: str
    version: str = "1.0.0"
    category: CapabilityCategory
    capabilities: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    risk_level: str = "LOW" # LOW, MEDIUM, HIGH
    min_jarvis_version: str = "2.0.0"
    evaluation_score: float = 0.95
    is_installed: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
