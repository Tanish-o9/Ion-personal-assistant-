from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class SafetyDecision(BaseModel):
    allowed: bool
    action: str = "allow" # allow, warn, block, require_approval
    risk_level: str = "low"
    reason: Optional[str] = None

class QualityCheckResult(BaseModel):
    passed: bool
    confidence_level: str = "HIGH" # HIGH, MEDIUM, LOW, UNKNOWN
    unsupported_claims: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

class GuardrailResult(BaseModel):
    is_safe: bool
    is_grounded: bool
    confidence_level: str = "HIGH"
    safety_decision: SafetyDecision
    quality_check: QualityCheckResult
