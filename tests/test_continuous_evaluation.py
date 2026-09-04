"""
Unit Tests for Phase 63: Continuous Evaluation & Release Gates.
"""

import pytest
from orchestrator.evaluation import ContinuousEvaluationPipeline

def test_release_gate_evaluation():
    pipe = ContinuousEvaluationPipeline()

    # High quality, low latency, clean security -> PASS
    res_pass = pipe.evaluate_release_candidate(
        candidate_id="model_v2_1",
        candidate_type="model",
        quality_score=0.92,
        security_score=0.98,
        latency_ms=450.0,
        error_rate=0.01
    )
    assert res_pass["release_status"] == "PASS"
    assert len(res_pass["regressions"]) == 0

    # Low security score -> FAIL
    res_fail = pipe.evaluate_release_candidate(
        candidate_id="skill_v1_bad",
        candidate_type="skill",
        quality_score=0.88,
        security_score=0.70,  # Below 0.95 threshold
        latency_ms=500.0,
        error_rate=0.01
    )
    assert res_fail["release_status"] == "FAIL"
    assert len(res_fail["regressions"]) == 1

    # Minor latency regression -> REVIEW_REQUIRED
    res_review = pipe.evaluate_release_candidate(
        candidate_id="workflow_slow",
        candidate_type="workflow",
        quality_score=0.86,
        security_score=0.96,
        latency_ms=2500.0,  # Exceeds 2000ms threshold
        error_rate=0.01
    )
    assert res_review["release_status"] == "REVIEW_REQUIRED"
