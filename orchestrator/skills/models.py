from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class Skill(BaseModel):
    """
    High-level reusable agent capability / workflow that orchestrates tools.
    """
    name: str
    description: str
    capabilities: List[str] = Field(default_factory=list)
    required_tools: List[str] = Field(default_factory=list)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    risk_level: str = "low"                # low, medium, high, restricted
    execution_mode: str = "sync"           # sync, async, background
    version: str = "v1"
    enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "required_tools": self.required_tools,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "risk_level": self.risk_level,
            "execution_mode": self.execution_mode,
            "version": self.version,
            "enabled": self.enabled,
            "metadata": self.metadata,
        }
