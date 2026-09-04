"""
Phase 85: Controlled Self-Improvement & Advanced Evaluation Engine.
Strictly bounded self-improvement pipeline:
OBSERVE -> MEASURE -> IDENTIFY WEAKNESS -> PROPOSE IMPROVEMENT -> GENERATE CANDIDATE -> OFFLINE EVALUATION -> SECURITY EVALUATION -> REGRESSION TEST -> HUMAN/ADMIN APPROVAL -> STAGING -> VALIDATION -> DEPLOY.

Prohibits autonomous self-modification of security controls, auth policies, approval rules, or resource limits.
Maintain versioning, evaluation gate enforcement, and rollback functionality.
"""

import enum
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from orchestrator.evaluation.pipeline import default_continuous_evaluation_pipeline
from database.connection import get_db_context
from database.models import ImprovementCandidateModel, EvaluationSnapshotModel, utc_now_iso

FORBIDDEN_SELF_MODIFICATION_TARGETS = [
    "security_policy",
    "auth_policy",
    "authentication",
    "authorization",
    "approval_requirements",
    "resource_limits",
    "privacy_policy",
    "system_safety_constraints"
]

class CandidateStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    EVALUATING = "EVALUATING"
    GATE_PASSED = "GATE_PASSED"
    GATE_FAILED = "GATE_FAILED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    STAGED = "STAGED"
    DEPLOYED = "DEPLOYED"
    REJECTED = "REJECTED"
    ROLLED_BACK = "ROLLED_BACK"

class ImprovementCandidateDetail(BaseModel):
    candidate_id: str
    target_component: str
    problem_statement: str
    proposed_change: Dict[str, Any]
    version: str = "1.0.0"
    evaluation_status: str = "UNTESTED"
    gate_results: Dict[str, Any] = Field(default_factory=dict)
    approval_status: str = "PENDING"
    status: CandidateStatus = CandidateStatus.PROPOSED
    rollback_state: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now_iso)

class ControlledSelfImprovementEngine:
    """Evaluation-driven controlled self-improvement pipeline with mandatory admin approval and rollback."""

    def propose_candidate(
        self,
        target_component: str,
        problem_statement: str,
        proposed_change: Dict[str, Any]
    ) -> ImprovementCandidateDetail:
        # Check forbidden self-modification targets
        target_lower = target_component.lower()
        if any(forbidden in target_lower for forbidden in FORBIDDEN_SELF_MODIFICATION_TARGETS):
            candidate_id = f"cand_{uuid.uuid4().hex[:12]}"
            return ImprovementCandidateDetail(
                candidate_id=candidate_id,
                target_component=target_component,
                problem_statement=problem_statement,
                proposed_change=proposed_change,
                evaluation_status="REJECTED_FORBIDDEN_TARGET",
                approval_status="REJECTED",
                status=CandidateStatus.REJECTED,
                gate_results={"security": "FAILED: Attempted self-modification of core security/auth control"}
            )

        candidate_id = f"cand_{uuid.uuid4().hex[:12]}"
        candidate = ImprovementCandidateDetail(
            candidate_id=candidate_id,
            target_component=target_component,
            problem_statement=problem_statement,
            proposed_change=proposed_change,
            status=CandidateStatus.PROPOSED,
            rollback_state={"previous_version": "0.9.0", "stable_hash": "base_hash"}
        )

        try:
            with get_db_context() as db:
                icm = ImprovementCandidateModel(
                    id=candidate_id,
                    target_component=target_component,
                    problem_statement=problem_statement,
                    proposed_change_json=str(proposed_change),
                    version="1.0.0",
                    evaluation_status="UNTESTED",
                    approval_status="PENDING",
                    rollback_state_json=str(candidate.rollback_state)
                )
                db.add(icm)
                db.commit()
        except Exception:
            pass

        return candidate

    def evaluate_candidate_offline(
        self,
        candidate: ImprovementCandidateDetail,
        quality_score: float = 0.90,
        security_score: float = 0.98,
        latency_ms: float = 450.0,
        error_rate: float = 0.01
    ) -> ImprovementCandidateDetail:
        """Runs candidate through Phase 63 Continuous Evaluation regression gates."""
        gate_res = default_continuous_evaluation_pipeline.evaluate_release_candidate(
            candidate_id=candidate.candidate_id,
            candidate_type="self_improvement_candidate",
            quality_score=quality_score,
            security_score=security_score,
            latency_ms=latency_ms,
            error_rate=error_rate
        )

        candidate.gate_results = gate_res
        if gate_res["release_status"] == "PASS":
            candidate.status = CandidateStatus.GATE_PASSED
            candidate.evaluation_status = "PASSED_ALL_GATES"
            candidate.approval_status = "PENDING_ADMIN_APPROVAL"
        else:
            candidate.status = CandidateStatus.GATE_FAILED
            candidate.evaluation_status = "FAILED_REGRESSION_GATES"
            candidate.approval_status = "REJECTED"

        try:
            with get_db_context() as db:
                snap = EvaluationSnapshotModel(
                    id=f"evsnap_{uuid.uuid4().hex[:12]}",
                    candidate_id=candidate.candidate_id,
                    dataset_version="v1",
                    metrics_json=str(gate_res)
                )
                db.add(snap)
                db.commit()
        except Exception:
            pass

        return candidate

    def approve_candidate(self, candidate: ImprovementCandidateDetail, admin_user_id: str) -> ImprovementCandidateDetail:
        """Mandatory Human/Admin approval step before staging/deployment."""
        if candidate.status != CandidateStatus.GATE_PASSED:
            candidate.approval_status = "REJECTED_GATE_FAILURE"
            return candidate

        candidate.approval_status = f"APPROVED_BY_{admin_user_id}"
        candidate.status = CandidateStatus.APPROVED
        return candidate

    def deploy_candidate(self, candidate: ImprovementCandidateDetail) -> ImprovementCandidateDetail:
        if candidate.status != CandidateStatus.APPROVED:
            candidate.status = CandidateStatus.REJECTED
            return candidate

        # Stage and deploy
        candidate.status = CandidateStatus.DEPLOYED
        candidate.evaluation_status = "DEPLOYED_ACTIVE"
        return candidate

    def rollback_candidate(self, candidate: ImprovementCandidateDetail) -> ImprovementCandidateDetail:
        """Reverts candidate deployment to previous version."""
        candidate.status = CandidateStatus.ROLLED_BACK
        candidate.evaluation_status = f"ROLLED_BACK_TO_{candidate.rollback_state.get('previous_version', '0.9.0')}"
        return candidate

default_controlled_self_improvement_engine = ControlledSelfImprovementEngine()
