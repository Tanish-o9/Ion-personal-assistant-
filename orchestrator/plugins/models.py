from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class PluginManifest(BaseModel):
    id: str
    name: str
    version: str = "1.0.0"
    author: Optional[str] = "Community"
    description: str
    capabilities: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list) # network_access, file_access, read_only
    compatibility_version: str = "2.0.0"

class PluginDefinition(BaseModel):
    manifest: PluginManifest
    enabled: bool = True
    installed_at: Optional[str] = None
