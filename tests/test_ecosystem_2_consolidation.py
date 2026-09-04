import pytest
from orchestrator.platform.ecosystem_consolidation import (
    UniversalSecurityBoundaryGuard,
    EcosystemHealthSignalEngine,
    EcosystemConsolidationEngine,
    default_ecosystem_consolidation_engine,
)

def test_universal_security_boundary_guard():
    guard = UniversalSecurityBoundaryGuard()
    res = guard.enforce_security_boundary("market_jira_connector", "user-1", "EXECUTE")
    assert res["auth"] == "PASSED"
    assert res["authorization"] == "PASSED"
    assert res["approval"] == "APPROVED"
    assert res["execution"] == "VERIFIED_SAFE"

def test_ecosystem_health_signal_engine():
    engine = EcosystemHealthSignalEngine()
    signals = engine.get_health_signals()
    assert len(signals) >= 6
    assert all(s.health_status == "HEALTHY" for s in signals)

def test_20_step_ecosystem_scenario_and_manifest():
    engine = EcosystemConsolidationEngine()
    steps = engine.run_20_step_ecosystem_scenario()
    assert len(steps) == 20
    assert all(s.passed for s in steps)

    manifest = engine.generate_ecosystem_manifest()
    assert manifest.jarvis_version == "v4.1.0"
    assert manifest.total_ecosystem_steps_tested == 20
    assert manifest.passed_steps == 20
    assert manifest.final_ecosystem_readiness_status == "READY"
