"""
Phase 85: Controlled Self-Improvement & Advanced Evaluation Engine Tests.
"""

import pytest
from orchestrator.learning.self_improvement import (
    CandidateStatus,
    ControlledSelfImprovementEngine,
    default_controlled_self_improvement_engine
)

def test_forbidden_target_rejection():
    # Attempting to modify security policy MUST be rejected
    cand = default_controlled_self_improvement_engine.propose_candidate(
        target_component="security_policy_enforcer",
        problem_statement="Bypass authentication requirement for speed",
        proposed_change={"allow_anonymous": True}
    )

    assert cand.status == CandidateStatus.REJECTED
    assert cand.approval_status == "REJECTED"
    assert "security" in cand.gate_results

def test_improvement_candidate_pipeline_pass_and_deploy():
    # Valid candidate for RAG chunking optimization
    cand = default_controlled_self_improvement_engine.propose_candidate(
        target_component="rag_chunking_strategy",
        problem_statement="Improve retrieval precision by adjusting chunk overlap from 50 to 100",
        proposed_change={"chunk_overlap": 100}
    )
    assert cand.status == CandidateStatus.PROPOSED

    # Offline evaluation passes
    evaluated = default_controlled_self_improvement_engine.evaluate_candidate_offline(
        cand, quality_score=0.92, security_score=0.99, latency_ms=350.0, error_rate=0.01
    )
    assert evaluated.status == CandidateStatus.GATE_PASSED
    assert evaluated.approval_status == "PENDING_ADMIN_APPROVAL"

    # Human/Admin Approval
    approved = default_controlled_self_improvement_engine.approve_candidate(evaluated, admin_user_id="admin_1")
    assert approved.status == CandidateStatus.APPROVED

    # Deployment
    deployed = default_controlled_self_improvement_engine.deploy_candidate(approved)
    assert deployed.status == CandidateStatus.DEPLOYED

    # Rollback
    rolled_back = default_controlled_self_improvement_engine.rollback_candidate(deployed)
    assert rolled_back.status == CandidateStatus.ROLLED_BACK

def test_regression_gate_failure_blocks_deployment():
    cand = default_controlled_self_improvement_engine.propose_candidate(
        target_component="tool_selection_router",
        problem_statement="Add experimental model routing",
        proposed_change={"model": "experimental-v1"}
    )

    # Offline evaluation fails security threshold (e.g. security_score=0.80 < 0.95)
    evaluated = default_controlled_self_improvement_engine.evaluate_candidate_offline(
        cand, quality_score=0.90, security_score=0.80, latency_ms=500.0, error_rate=0.01
    )
    assert evaluated.status == CandidateStatus.GATE_FAILED

    # Approval fails
    approved = default_controlled_self_improvement_engine.approve_candidate(evaluated, admin_user_id="admin_1")
    assert approved.approval_status == "REJECTED_GATE_FAILURE"
