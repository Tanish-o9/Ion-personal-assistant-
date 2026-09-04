"""
Unit Tests for Phase 56: Advanced Reasoning Engine.
"""

import pytest
from orchestrator.reasoning import (
    AdvancedReasoningEngine,
    ReasoningStrategy,
    ReasoningContext,
    EvidenceItem,
)

def test_strategy_selection():
    engine = AdvancedReasoningEngine()

    ctx_simple = ReasoningContext(task="What time is it?")
    assert engine.select_strategy(ctx_simple) == ReasoningStrategy.DIRECT

    ctx_compare = ReasoningContext(task="Compare PostgreSQL versus SQLite")
    assert engine.select_strategy(ctx_compare) == ReasoningStrategy.COMPARE

    ctx_limit = ReasoningContext(task="Complex task", current_iteration=5, max_reasoning_iterations=5)
    assert engine.select_strategy(ctx_limit) == ReasoningStrategy.ASK_USER

def test_evidence_analysis_and_conflict_detection():
    engine = AdvancedReasoningEngine()

    # Empty evidence -> UNCERTAIN
    ctx_empty = ReasoningContext(task="Check facts")
    res_empty = engine.analyze_evidence(ctx_empty)
    assert res_empty["status"] == "UNCERTAIN"

    # Conflicting evidence
    ctx_conflict = ReasoningContext(
        task="Check status",
        evidence=[
            EvidenceItem(source="SrcA", content="System is operational"),
            EvidenceItem(source="SrcB", content="System is not operational")
        ]
    )
    res_conflict = engine.analyze_evidence(ctx_conflict)
    assert res_conflict["status"] == "CONFLICTING"
    assert len(res_conflict["conflicts"]) == 1

    # Verified evidence
    ctx_valid = ReasoningContext(
        task="Check status",
        evidence=[
            EvidenceItem(source="SrcA", content="Version 1.0 released", confidence=0.9),
            EvidenceItem(source="SrcB", content="Version 1.0 details", confidence=0.8)
        ]
    )
    res_valid = engine.analyze_evidence(ctx_valid)
    assert res_valid["status"] == "VERIFIED"
    assert res_valid["confidence"] == 0.85
