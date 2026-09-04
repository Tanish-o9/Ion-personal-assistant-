from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AgentDefinition(BaseModel):
    name: str
    description: str
    capabilities: List[str] = Field(default_factory=list)
    allowed_skills: List[str] = Field(default_factory=list)
    allowed_tools: List[str] = Field(default_factory=list)
    risk_level: str = "low"
    model_preference: Optional[str] = None

class TaskDelegation(BaseModel):
    task_id: str
    parent_task_id: Optional[str] = None
    agent_name: str
    objective: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    status: str = "pending" # pending, running, completed, failed

class AgentResult(BaseModel):
    task_id: str
    agent_name: str
    status: str # success, failed
    findings: str
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_category: str = "high" # high, medium, low
    errors: Optional[str] = None
