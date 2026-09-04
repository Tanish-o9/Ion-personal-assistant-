"""
Phase 83: Simulation & Scenario Models.
"""

import enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ScenarioType(str, enum.Enum):
    BASELINE = "BASELINE"
    BEST_CASE = "BEST_CASE"
    EXPECTED = "EXPECTED"
    WORST_CASE = "WORST_CASE"
    CUSTOM = "CUSTOM"

class SimulationRule(BaseModel):
    name: str
    variable: str
    operation: str  # add, multiply, set, threshold
    value: float
    description: Optional[str] = None

class SimulationConfig(BaseModel):
    scenario_type: ScenarioType = ScenarioType.BASELINE
    iterations: int = 100
    seed: int = 42
    max_runtime_sec: float = 30.0
    max_memory_mb: float = 512.0

class SimulationRunResult(BaseModel):
    run_id: str
    simulation_id: str
    scenario_type: ScenarioType
    seed: int
    iterations: int
    initial_state: Dict[str, Any]
    final_state: Dict[str, Any]
    metrics: Dict[str, Any] = Field(default_factory=dict)
    label: str = "SIMULATED"  # Always tagged SIMULATED
    assumptions: List[str] = Field(default_factory=list)
