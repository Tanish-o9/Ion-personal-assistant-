"""
Phase 73: Decision Intelligence Data Models
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class DecisionCriterion(BaseModel):
    name: str
    weight: float = 1.0  # 0.0 to 1.0
    description: Optional[str] = None

class DecisionRisk(BaseModel):
    risk_title: str
    severity: str  # HIGH, MEDIUM, LOW
    mitigation: str

class DecisionOption(BaseModel):
    option_id: str
    title: str
    description: str
    scores: Dict[str, float] = Field(default_factory=dict)  # criterion_name -> score (0.0 to 1.0)
    weighted_score: float = 0.0
    benefits: List[str] = Field(default_factory=list)
    risks: List[DecisionRisk] = Field(default_factory=list)
    costs_usd: float = 0.0

class DecisionScenario(BaseModel):
    scenario_name: str  # Best Case, Expected Case, Worst Case
    description: str
    predicted_outcome: str

class DecisionRecommendation(BaseModel):
    recommended_option_id: str
    summary_rationale: str
    gains: List[str]
    tradeoffs: List[str]
    risk_shifts: List[str]
    missing_information: List[str]
    consequential_warning: Optional[str] = None

class DecisionModel(BaseModel):
    decision_id: str
    question: str
    options: List[DecisionOption]
    criteria: List[DecisionCriterion]
    constraints: List[str] = Field(default_factory=list)
    confidence_level: str = "MEDIUM"  # HIGH, MEDIUM, LOW, UNKNOWN
    scenarios: List[DecisionScenario] = Field(default_factory=list)
    recommendation: DecisionRecommendation

class WhatIfQuery(BaseModel):
    variable_name: str
    baseline_value: Any
    modified_value: Any
    assumptions_changed: List[str] = Field(default_factory=list)

class SensitivityAnalysisResult(BaseModel):
    variable_name: str
    sensitivity_impact: float = 0.0  # 0.0 to 1.0
    delta_score: float = 0.0
    ranking: int = 1

class ScenarioMatrixRow(BaseModel):
    option_title: str
    cost_usd: float = 0.0
    risk_level: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    benefit_score: float = 0.0
    uncertainty_level: str = "MEDIUM"
    resource_usage: str = "NORMAL"
    outcome_summary: str = ""

class DecisionExperimentResult(BaseModel):
    experiment_id: str
    question: str
    baseline_state: Dict[str, Any] = Field(default_factory=dict)
    what_if_queries: List[WhatIfQuery] = Field(default_factory=list)
    sensitivity: List[SensitivityAnalysisResult] = Field(default_factory=list)
    matrix: List[ScenarioMatrixRow] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    recommendation: DecisionRecommendation
    audit_trail: Dict[str, Any] = Field(default_factory=dict)  # Operational metadata (no hidden CoT)

class DecisionEvaluationResult(BaseModel):
    criteria_correctness: float
    arithmetic_accuracy: float
    assumption_transparency: float
    recommendation_consistency: float
    uncertainty_handling: float


