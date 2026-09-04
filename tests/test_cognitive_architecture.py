"""
Unit Tests for Phase 66: Cognitive Architecture 2.0.
"""

import pytest
from database.connection import init_db
from orchestrator.context.cognitive import CognitiveManager
from orchestrator.memory import default_memory_manager

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def test_cognitive_context_assembly_and_compression():
    cm = CognitiveManager()
    user_id = "user_cog_1"
    session_id = "sess_cog_1"

    default_memory_manager.save_memory(user_id, "User prefers dark mode UI", "preference", importance=5)

    cog = cm.assemble_cognitive_context(
        user_id=user_id,
        session_id=session_id,
        current_request="Build dashboard",
        goal_description="Create high performance analytics UI"
    )

    assert cog.user_id == user_id
    assert len(cog.relevant_memory) >= 1

    compressed = cm.compress_cognitive_context(cog)
    assert compressed["user_id"] == user_id
    assert len(compressed["key_facts"]) >= 2
    assert "active_constraints" in compressed

def test_cognitive_conflict_detection():
    cm = CognitiveManager()
    user_id = "user_cog_2"
    session_id = "sess_cog_2"

    default_memory_manager.save_memory(user_id, "PostgreSQL database is enabled", "fact")

    cog = cm.assemble_cognitive_context(
        user_id=user_id,
        session_id=session_id,
        current_request="Database check"
    )

    # Conflict check
    res = cm.detect_cognitive_conflicts(cog, "PostgreSQL database is not enabled")
    assert res["status"] == "CONFLICT_DETECTED"
    assert res["uncertainty"] == 0.85

