from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class EcosystemCatalogEntry(BaseModel):
    capability_id: str
    name: str
    description: str
    capability_type: str # plugin, tool, skill
    version: str = "1.0.0"
    author: str = "Community"
    required_permissions: List[str] = Field(default_factory=list)
    risk_level: str = "low"
    evaluation_status: str = "pending" # pending, passed, rejected
    enabled: bool = True
