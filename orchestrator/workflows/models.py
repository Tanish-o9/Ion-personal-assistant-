"""
Phase 60: Workflow Builder Models & Enums.
"""

import enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class WorkflowNodeType(str, enum.Enum):
    TRIGGER = "TRIGGER"
    INPUT = "INPUT"
    LLM = "LLM"
    RESEARCH = "RESEARCH"
    RAG = "RAG"
    TOOL = "TOOL"
    SKILL = "SKILL"
    AGENT = "AGENT"
    CONDITION = "CONDITION"
    APPROVAL = "APPROVAL"
    TRANSFORM = "TRANSFORM"
    OUTPUT = "OUTPUT"

class WorkflowNode(BaseModel):
    id: str
    type: WorkflowNodeType
    label: str
    config: Dict[str, Any] = Field(default_factory=dict)

class WorkflowEdge(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    condition_expr: Optional[str] = None

class WorkflowDefinition(BaseModel):
    id: str
    user_id: str
    workspace_id: Optional[str] = None
    name: str
    description: str = ""
    version: int = 1
    nodes: List[WorkflowNode] = Field(default_factory=list)
    edges: List[WorkflowEdge] = Field(default_factory=list)
    is_enabled: bool = True
