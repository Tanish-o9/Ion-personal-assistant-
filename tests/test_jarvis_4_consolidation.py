import pytest
from orchestrator.platform.consolidation import (
    JarvisConsolidationAuditor,
    DuplicateCodeDetector,
    SecurityPrivacyAuditor,
    CertificationSuite,
    ReleaseManifestGenerator,
    JarvisConsolidationEngine,
    default_consolidation_engine,
)

def test_consolidation_auditor():
    auditor = JarvisConsolidationAuditor()
    subsystems = auditor.audit_all_subsystems()
    assert len(subsystems) == 29
    assert all(s.status == "OPERATIONAL" for s in subsystems)

def test_duplicate_code_detector():
    detector = DuplicateCodeDetector()
    report = detector.audit_duplicates()
    assert report.duplicate_count == 0
    assert "PASSED" in report.status

def test_security_privacy_auditor():
    sec_auditor = SecurityPrivacyAuditor()
    report = sec_auditor.run_security_audit()
    assert report.tenant_isolation_verified is True
    assert report.overall_status == "PASSED"

def test_50_certification_scenarios():
    suite = CertificationSuite()
    scenarios = suite.run_50_certification_scenarios()
    assert len(scenarios) == 50
    assert all(s.passed for s in scenarios)

def test_full_consolidation_engine_manifest():
    engine = JarvisConsolidationEngine()
    manifest = engine.run_full_consolidation_audit()
    assert manifest.jarvis_version == "v4.0.0"
    assert manifest.certification_results["total_scenarios"] == 50
    assert manifest.certification_results["passed_scenarios"] == 50
    assert manifest.security_status == "PASSED"
    assert manifest.final_readiness_status == "READY"
