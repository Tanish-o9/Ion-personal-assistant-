"""
Phase 56: Advanced Reasoning Engine Models & Enums.
"""

import enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ReasoningStrategy(str, enum.Enum):
    DIRECT = "DIRECT"
    DECOMPOSE = "DECOMPOSE"
    COMPARE = "COMPARE"
    VERIFY = "VERIFY"
    RESEARCH = "RESEARCH"
    REPLAN = "REPLAN"
    ASK_USER = "ASK_USER"

class EvidenceItem(BaseModel):
    source: str
    content: str
    confidence: float = 1.0
    timestamp: Optional[str] = None

class ReasoningContext(BaseModel):
    task: str
    goal_id: Optional[str] = None
    constraints: List[str] = Field(default_factory=list)
    available_capabilities: List[str] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    tool_results: Dict[str, Any] = Field(default_factory=dict)
    previous_results: List[Dict[str, Any]] = Field(default_factory=list)
    uncertainty: float = 0.0  # 0.0 = certain, 1.0 = completely uncertain
    max_reasoning_iterations: int = 5
    current_iteration: int = 0
    verification_status: str = "UNVERIFIED" # UNVERIFIED, VERIFIED, CONFLICTING, UNCERTAIN

class EvidenceClassification(str, enum.Enum):
    OBSERVATIONAL = "OBSERVATIONAL"
    EXPERIMENTAL = "EXPERIMENTAL"
    QUASI_EXPERIMENTAL = "QUASI_EXPERIMENTAL"
    THEORETICAL = "THEORETICAL"
    EXPERT_INTERPRETATION = "EXPERT_INTERPRETATION"
    UNKNOWN = "UNKNOWN"

class CausalVariable(BaseModel):
    name: str
    type: str = "continuous"  # continuous, discrete, categorical, binary
    description: Optional[str] = None

class CausalRelationship(BaseModel):
    cause: str
    effect: str
    strength: float = 0.5  # 0.0 to 1.0
    evidence_type: EvidenceClassification = EvidenceClassification.OBSERVATIONAL
    description: Optional[str] = None

class Confounder(BaseModel):
    name: str
    affects_cause: str
    affects_effect: str
    plausible_explanation: str

class CausalClaim(BaseModel):
    claim: str
    evidence: List[EvidenceItem] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    alternative_explanations: List[str] = Field(default_factory=list)
    confounders: List[Confounder] = Field(default_factory=list)
    uncertainty: float = 0.2
    is_correlation_only: bool = False


