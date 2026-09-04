"""
FastAPI Router for JARVIS 4.2 (Phases 81–85).
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from orchestrator.goals.manager import default_goal_manager
from orchestrator.reasoning.causal import default_causal_analyzer, CausalGraph
from orchestrator.reasoning.models import EvidenceItem
from orchestrator.simulation.engine import default_simulation_engine
from orchestrator.simulation.models import SimulationRule, SimulationConfig, ScenarioType
from orchestrator.decision.experiments import default_decision_experiment_manager
from orchestrator.learning.self_improvement import default_controlled_self_improvement_engine

router = APIRouter(prefix="/api/v1", tags=["JARVIS 4.2 Advanced Reasoning"])

# Payload schemas
class CausalAnalyzeRequest(BaseModel):
    cause: str
    effect: str
    evidence_texts: List[str]

class SimulationRunRequest(BaseModel):
    initial_state: Dict[str, Any]
    rules: List[Dict[str, Any]]
    scenario_type: str = "BASELINE"
    iterations: int = 100
    seed: int = 42

class DecisionExperimentRequest(BaseModel):
    question: str
    baseline_state: Dict[str, Any]
    alternatives: List[Dict[str, Any]]
    constraints: List[str] = []

class ImprovementCandidateRequest(BaseModel):
    target_component: str
    problem_statement: str
    proposed_change: Dict[str, Any]


@router.get("/goals/{goal_id}/milestones")
def get_goal_milestones(goal_id: str, user_id: str = "default_user"):
    goal = default_goal_manager.get_goal(goal_id, user_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"goal_id": goal_id, "milestones": [m.model_dump() for m in goal.milestones]}


@router.post("/causal/analyze")
def analyze_causal_relationship(req: CausalAnalyzeRequest):
    evidence = [EvidenceItem(source="api", content=txt) for txt in req.evidence_texts]
    claim = default_causal_analyzer.evaluate_relationship(req.cause, req.effect, evidence)
    return claim.model_dump()


@router.post("/simulations/{simulation_id}/run")
def run_simulation(simulation_id: str, req: SimulationRunRequest):
    rules = [SimulationRule(**r) for r in req.rules]
    cfg = SimulationConfig(
        scenario_type=ScenarioType(req.scenario_type),
        iterations=req.iterations,
        seed=req.seed
    )
    res = default_simulation_engine.run_deterministic_simulation(simulation_id, req.initial_state, rules, cfg)
    return res.model_dump()


@router.post("/decision-experiments")
def create_decision_experiment(req: DecisionExperimentRequest, user_id: str = "default_user"):
    res = default_decision_experiment_manager.run_experiment(
        user_id=user_id,
        question=req.question,
        baseline_state=req.baseline_state,
        alternatives=req.alternatives,
        constraints=req.constraints
    )
    return res.model_dump()


@router.post("/improvement-candidates")
def propose_improvement_candidate(req: ImprovementCandidateRequest):
    cand = default_controlled_self_improvement_engine.propose_candidate(
        target_component=req.target_component,
        problem_statement=req.problem_statement,
        proposed_change=req.proposed_change
    )
    return cand.model_dump()


@router.post("/improvement-candidates/{candidate_id}/evaluate")
def evaluate_improvement_candidate(candidate_id: str, quality_score: float = 0.90, security_score: float = 0.98):
    # Dummy retrieval for API route
    from orchestrator.learning.self_improvement import ImprovementCandidateDetail, CandidateStatus
    dummy_cand = ImprovementCandidateDetail(
        candidate_id=candidate_id,
        target_component="rag_chunking",
        problem_statement="Optimize chunking",
        proposed_change={"overlap": 100},
        status=CandidateStatus.PROPOSED
    )
    res = default_controlled_self_improvement_engine.evaluate_candidate_offline(
        dummy_cand, quality_score=quality_score, security_score=security_score
    )
    return res.model_dump()


@router.post("/improvement-candidates/{candidate_id}/approve")
def approve_improvement_candidate(candidate_id: str, admin_user_id: str = "admin_1"):
    from orchestrator.learning.self_improvement import ImprovementCandidateDetail, CandidateStatus
    dummy_cand = ImprovementCandidateDetail(
        candidate_id=candidate_id,
        target_component="rag_chunking",
        problem_statement="Optimize chunking",
        proposed_change={"overlap": 100},
        status=CandidateStatus.GATE_PASSED
    )
    res = default_controlled_self_improvement_engine.approve_candidate(dummy_cand, admin_user_id=admin_user_id)
    return res.model_dump()
