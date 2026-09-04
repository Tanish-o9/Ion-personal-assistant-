"""
Phase 83: Simulation & Scenario Engine Tests.
"""

import pytest
from orchestrator.simulation.models import ScenarioType, SimulationRule, SimulationConfig
from orchestrator.simulation.engine import SimulationEngine, default_simulation_engine

def test_deterministic_simulation():
    rules = [
        SimulationRule(name="Increase Users", variable="users", operation="add", value=10.0),
        SimulationRule(name="Scale Revenue", variable="revenue", operation="multiply", value=1.05)
    ]
    initial = {"users": 100.0, "revenue": 1000.0}
    config = SimulationConfig(scenario_type=ScenarioType.BASELINE, iterations=5)

    res = default_simulation_engine.run_deterministic_simulation("sim_001", initial, rules, config)
    assert res.label == "SIMULATED"
    assert res.final_state["users"] == 150.0
    assert res.final_state["revenue"] > 1000.0
    assert res.metrics["iterations_completed"] == 5

def test_probabilistic_simulation_reproducibility():
    rules = [
        SimulationRule(name="Server Traffic Jitter", variable="requests", operation="add", value=50.0)
    ]
    initial = {"requests": 500.0}
    cfg1 = SimulationConfig(seed=123, iterations=10)
    cfg2 = SimulationConfig(seed=123, iterations=10)

    r1 = default_simulation_engine.run_probabilistic_simulation("sim_002", initial, rules, cfg1)
    r2 = default_simulation_engine.run_probabilistic_simulation("sim_002", initial, rules, cfg2)

    assert r1.final_state["requests"] == r2.final_state["requests"]
    assert r1.label == "SIMULATED"

def test_scenario_comparison():
    rules = [
        SimulationRule(name="Resource Usage", variable="cpu_usage", operation="add", value=5.0)
    ]
    initial = {"cpu_usage": 20.0}
    comparison = default_simulation_engine.compare_scenarios("sim_003", initial, rules)

    assert "BASELINE" in comparison
    assert "BEST_CASE" in comparison
    assert "EXPECTED" in comparison
    assert "WORST_CASE" in comparison
    assert comparison["BEST_CASE"].label == "SIMULATED"
