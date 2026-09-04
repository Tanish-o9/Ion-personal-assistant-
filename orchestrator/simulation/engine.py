"""
Phase 83: Simulation & Scenario Engine.
Executes safe, bounded deterministic and probabilistic software/data simulations.
All outputs are strictly tagged SIMULATED with zero direct external side-effects.
"""

import random
import time
import uuid
from typing import Dict, Any, List, Optional
from orchestrator.simulation.models import (
    ScenarioType,
    SimulationRule,
    SimulationConfig,
    SimulationRunResult
)
from database.connection import get_db_context
from database.models import SimulationModel, SimulationRunModel, utc_now_iso

class SimulationEngine:
    """Safe software sandbox for modeling hypothetical scenarios."""

    def run_deterministic_simulation(
        self,
        simulation_id: str,
        initial_state: Dict[str, Any],
        rules: List[SimulationRule],
        config: Optional[SimulationConfig] = None
    ) -> SimulationRunResult:
        config = config or SimulationConfig()
        start_time = time.time()

        state = dict(initial_state)
        # Apply deterministic rules over bounded iterations
        iterations = min(config.iterations, 10000)

        for i in range(iterations):
            if time.time() - start_time > config.max_runtime_sec:
                break
            for rule in rules:
                val = state.get(rule.variable, 0.0)
                if rule.operation == "add":
                    state[rule.variable] = val + rule.value
                elif rule.operation == "multiply":
                    state[rule.variable] = val * rule.value
                elif rule.operation == "set":
                    state[rule.variable] = rule.value
                elif rule.operation == "threshold":
                    state[rule.variable] = max(val, rule.value)

        run_id = f"simrun_{uuid.uuid4().hex[:12]}"
        metrics = {
            "execution_time_sec": round(time.time() - start_time, 4),
            "iterations_completed": iterations,
            "rules_applied": len(rules)
        }

        result = SimulationRunResult(
            run_id=run_id,
            simulation_id=simulation_id,
            scenario_type=config.scenario_type,
            seed=config.seed,
            iterations=iterations,
            initial_state=initial_state,
            final_state=state,
            metrics=metrics,
            label="SIMULATED",
            assumptions=["System transitions follow deterministic state transformation rules", "Environment isolated from external network side-effects"]
        )

        # Store run in database if valid DB context exists
        try:
            with get_db_context() as db:
                run_model = SimulationRunModel(
                    id=run_id,
                    simulation_id=simulation_id,
                    scenario_type=config.scenario_type.value,
                    seed=config.seed,
                    iterations=iterations,
                    results_json=str(state),
                    metrics_json=str(metrics)
                )
                db.add(run_model)
                db.commit()
        except Exception:
            pass  # Standalone test fallback

        return result

    def run_probabilistic_simulation(
        self,
        simulation_id: str,
        initial_state: Dict[str, Any],
        rules: List[SimulationRule],
        config: Optional[SimulationConfig] = None
    ) -> SimulationRunResult:
        config = config or SimulationConfig()
        rng = random.Random(config.seed)
        start_time = time.time()

        state = dict(initial_state)
        iterations = min(config.iterations, 5000)

        for i in range(iterations):
            if time.time() - start_time > config.max_runtime_sec:
                break
            for rule in rules:
                val = state.get(rule.variable, 0.0)
                # Introduce bounded probabilistic variation using seed
                jitter = rng.uniform(0.95, 1.05)
                if rule.operation == "add":
                    state[rule.variable] = val + (rule.value * jitter)
                elif rule.operation == "multiply":
                    state[rule.variable] = val * (rule.value * jitter)

        run_id = f"simrun_{uuid.uuid4().hex[:12]}"
        metrics = {
            "execution_time_sec": round(time.time() - start_time, 4),
            "iterations_completed": iterations,
            "seed": config.seed
        }

        return SimulationRunResult(
            run_id=run_id,
            simulation_id=simulation_id,
            scenario_type=config.scenario_type,
            seed=config.seed,
            iterations=iterations,
            initial_state=initial_state,
            final_state=state,
            metrics=metrics,
            label="SIMULATED",
            assumptions=[f"Probabilistic variance bounded by reproducible seed {config.seed}"]
        )

    def compare_scenarios(
        self,
        simulation_id: str,
        initial_state: Dict[str, Any],
        rules: List[SimulationRule]
    ) -> Dict[str, SimulationRunResult]:
        scenarios = {
            ScenarioType.BASELINE: SimulationConfig(scenario_type=ScenarioType.BASELINE, iterations=50),
            ScenarioType.BEST_CASE: SimulationConfig(scenario_type=ScenarioType.BEST_CASE, iterations=100),
            ScenarioType.EXPECTED: SimulationConfig(scenario_type=ScenarioType.EXPECTED, iterations=75),
            ScenarioType.WORST_CASE: SimulationConfig(scenario_type=ScenarioType.WORST_CASE, iterations=25),
        }

        results = {}
        for stype, cfg in scenarios.items():
            results[stype.value] = self.run_deterministic_simulation(simulation_id, initial_state, rules, cfg)
        return results

default_simulation_engine = SimulationEngine()
