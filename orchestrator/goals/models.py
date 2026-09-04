"""
Phase 55: Goal Models & Enums.
"""

import enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class GoalStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PLANNED = "PLANNED"
    RUNNING = "RUNNING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class GoalHorizonLimits(BaseModel):
    max_milestones: int = 5
    max_tasks: int = 15
    max_steps: int = 30
    max_replans: int = 3
    max_runtime_sec: float = 3600.0
    max_cost_usd: float = 10.0
    max_tool_calls: int = 50
    max_llm_calls: int = 100

class GoalTaskStep(BaseModel):
    step_number: int
    title: str
    agent_type: str = "general"
    tool_name: Optional[str] = None
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    result: Optional[str] = None

class GoalTask(BaseModel):
    id: str
    title: str
    dependencies: List[str] = Field(default_factory=list)
    steps: List[GoalTaskStep] = Field(default_factory=list)
    status: str = "PENDING"
    can_parallel: bool = False

class GoalMilestone(BaseModel):
    id: str
    title: str
    tasks: List[GoalTask] = Field(default_factory=list)
    status: str = "PENDING"
    expected_outcome: Optional[str] = None
    actual_outcome: Optional[str] = None

class GoalCreatePayload(BaseModel):
    description: str
    success_criteria: List[str] = Field(default_factory=list)
    workspace_id: Optional[str] = None
    max_steps: int = 20
    max_budget_usd: float = 5.0
    constraints: List[str] = Field(default_factory=list)
    priority: str = "MEDIUM"
    risk_tolerance: str = "LOW"
    horizon_limits: Optional[GoalHorizonLimits] = None

class GoalDetail(BaseModel):
    id: str
    user_id: str
    workspace_id: Optional[str] = None
    description: str
    success_criteria: List[str] = Field(default_factory=list)
    status: GoalStatus = GoalStatus.DRAFT
    current_step: int = 0
    total_steps: int = 0
    max_steps: int = 20
    max_budget_usd: float = 5.0
    consumed_budget_usd: float = 0.0
    constraints: List[str] = Field(default_factory=list)
    priority: str = "MEDIUM"
    risk_tolerance: str = "LOW"
    replan_count: int = 0
    horizon_limits: GoalHorizonLimits = Field(default_factory=GoalHorizonLimits)
    milestones: List[GoalMilestone] = Field(default_factory=list)
    steps: List[GoalTaskStep] = Field(default_factory=list)
    checkpoint_state: Dict[str, Any] = Field(default_factory=dict)

