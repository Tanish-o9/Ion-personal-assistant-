"""
Phase 82: Causal Reasoning Engine Tests.
"""

import pytest
from orchestrator.reasoning.causal import CausalGraph, CausalAnalyzer, default_causal_analyzer
from orchestrator.reasoning.models import (
    CausalVariable,
    CausalRelationship,
    EvidenceClassification,
    EvidenceItem
)

def test_causal_graph_and_confounders():
    graph = CausalGraph()
    # Confounder D affects both A and B
    graph.add_relationship(CausalRelationship(cause="D", effect="A"))
    graph.add_relationship(CausalRelationship(cause="D", effect="B"))
    graph.add_relationship(CausalRelationship(cause="A", effect="B"))

    confounders = default_causal_analyzer.detect_confounders("A", "B", graph)
    assert len(confounders) == 1
    assert confounders[0].name == "D"

def test_correlation_vs_causation_claim():
    graph = CausalGraph()
    graph.add_relationship(CausalRelationship(cause="Weather", effect="IceCreamSales"))
    graph.add_relationship(CausalRelationship(cause="Weather", effect="DrowningIncidents"))
    graph.add_relationship(CausalRelationship(cause="IceCreamSales", effect="DrowningIncidents"))

    evidence = [EvidenceItem(source="survey", content="Observed strong positive correlation between ice cream sales and drowning incidents.")]
    claim = default_causal_analyzer.evaluate_relationship("IceCreamSales", "DrowningIncidents", evidence, graph)

    assert claim.is_correlation_only is True
    assert len(claim.confounders) == 1
    assert claim.confounders[0].name == "Weather"

def test_intervention_reasoning():
    graph = CausalGraph()
    graph.add_relationship(CausalRelationship(cause="AdSpend", effect="WebTraffic"))
    graph.add_relationship(CausalRelationship(cause="WebTraffic", effect="Revenue"))

    result = default_causal_analyzer.evaluate_intervention("AdSpend", 5000, graph)
    assert result["target_variable"] == "AdSpend"
    assert "WebTraffic" in result["downstream_affected_variables"]
    assert "SIMULATED" not in result["intervention"]

def test_counterfactual_analysis():
    observed = {"price": 100, "sales": 500, "marketing_budget": 1000}
    counterfactual = {"price": 80}

    res = default_causal_analyzer.counterfactual_analysis(observed, counterfactual)
    assert "price" in res["modified_variables"]
    assert res["modified_variables"]["price"]["observed"] == 100
    assert res["modified_variables"]["price"]["counterfactual"] == 80
    assert len(res["counterfactual_assumptions"]) >= 2
