import pytest
from orchestrator.decision.models import DecisionOption, DecisionCriterion, DecisionRisk
from orchestrator.decision.engine import (
    DecisionIntelligenceEngine,
    WeightedCriteriaEvaluator,
    default_decision_intelligence_engine,
)

def test_weighted_criteria_evaluator():
    evaluator = WeightedCriteriaEvaluator()
    criteria = [
        DecisionCriterion(name="performance", weight=2.0),
        DecisionCriterion(name="cost", weight=1.0),
    ]
    options = [
        DecisionOption(option_id="opt1", title="Option A", description="Desc A", scores={"performance": 0.9, "cost": 0.5}),
        DecisionOption(option_id="opt2", title="Option B", description="Desc B", scores={"performance": 0.6, "cost": 0.9}),
    ]

    evaluated = evaluator.evaluate_options(options, criteria)
    # Option A weighted: (2.0 * 0.9 + 1.0 * 0.5) / 3.0 = (1.8 + 0.5) / 3 = 0.767
    # Option B weighted: (2.0 * 0.6 + 1.0 * 0.9) / 3.0 = (1.2 + 0.9) / 3 = 0.7
    assert evaluated[0].option_id == "opt1"
    assert round(evaluated[0].weighted_score, 2) == 0.77

def test_decision_intelligence_matrix_and_consequence():
    engine = DecisionIntelligenceEngine()
    options = [
        DecisionOption(
            option_id="postgres",
            title="PostgreSQL HA",
            description="Relational database cluster",
            scores={"performance": 0.85, "cost_efficiency": 0.7, "reliability": 0.95},
            risks=[DecisionRisk(risk_title="Failover delay", severity="MEDIUM", mitigation="Prometheus + Patroni")],
        ),
        DecisionOption(
            option_id="dynamo",
            title="NoSQL Cloud DB",
            description="Managed NoSQL store",
            scores={"performance": 0.9, "cost_efficiency": 0.5, "reliability": 0.9},
        ),
    ]

    model = engine.build_decision_matrix(
        decision_id="dec-1",
        question="Which primary database strategy should JARVIS adopt?",
        options=options,
        criteria=[],
        is_high_consequence=True,
    )

    assert model.recommendation.recommended_option_id == "postgres"
    assert model.recommendation.consequential_warning is not None
    assert "Consequential Decision Intelligence" in model.recommendation.consequential_warning
    assert len(model.scenarios) == 3

    eval_res = engine.evaluate_decision_quality(model)
    assert eval_res.arithmetic_accuracy == 1.0
