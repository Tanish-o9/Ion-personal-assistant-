"""
Phase 84: Decision Experiments & What-If Engine Tests.
"""

import pytest
from orchestrator.decision.experiments import DecisionExperimentManager, default_decision_experiment_manager

def test_decision_experiment_what_if_and_sensitivity():
    baseline = {"cloud_monthly_cost": 5000.0, "latency_ms": 120.0}
    alternatives = [
        {"name": "Option A: Reserved Instances", "target_variable": "cloud_monthly_cost", "value": 3200.0, "cost_usd": 3200.0, "benefit_score": 0.85},
        {"name": "Option B: Multi-Region Failover", "target_variable": "latency_ms", "value": 45.0, "cost_usd": 7500.0, "benefit_score": 0.95}
    ]

    res = default_decision_experiment_manager.run_experiment(
        user_id="test_exp_user",
        question="Should we switch to Reserved Instances or Multi-Region Failover?",
        baseline_state=baseline,
        alternatives=alternatives,
        constraints=["Max monthly budget $8000"]
    )

    assert res.experiment_id.startswith("decexp_")
    assert len(res.what_if_queries) == 2
    assert len(res.sensitivity) == 2
    assert res.sensitivity[0].variable_name == "cloud_monthly_cost"
    assert len(res.matrix) == 2
    assert res.matrix[0].option_title == "Option A: Reserved Instances"
    assert res.recommendation.recommended_option_id == "Option A: Reserved Instances"

def test_missing_information_detection():
    baseline = {"service_name": "API Gateway"}
    alternatives = [
        {"name": "Option 1", "target_variable": "replicas", "value": 5}
    ]
    res = default_decision_experiment_manager.run_experiment(
        user_id="test_exp_user",
        question="Scale replicas?",
        baseline_state=baseline,
        alternatives=alternatives,
        constraints=[]
    )

    assert len(res.missing_information) >= 2
    assert "budget" in res.missing_information[0].lower() or "cost" in res.missing_information[0].lower()
