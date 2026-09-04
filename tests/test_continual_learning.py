"""
Unit & Integration Tests for Phase 53: Continual Learning & Advanced Agent Memory.
"""

import pytest
from orchestrator.learning import LearningManager

def test_workflow_learning_and_reliability_scores():
    lm = LearningManager()
    user_id = "user_test_p53"
    session_id = "sess_p53"

    # Record 2 successful executions of Skill A + Tool X
    lm.record_execution(user_id=user_id, session_id=session_id, task_type="code_generation", skill_used="Skill_A", tools_used=["tool_x", "tool_y"], outcome="success")
    lm.record_execution(user_id=user_id, session_id=session_id, task_type="code_generation", skill_used="Skill_A", tools_used=["tool_x"], outcome="success")

    # Record 1 failed execution of Skill B + Tool Z
    lm.record_execution(user_id=user_id, session_id=session_id, task_type="code_generation", skill_used="Skill_B", tools_used=["tool_z"], outcome="failed")

    reliability = lm.get_workflow_reliability("code_generation", user_id)
    assert reliability["recommended_skill"] == "Skill_A"
    assert reliability["tool_scores"].get("tool_x") == 1.0
    assert reliability["tool_scores"].get("tool_z") == 0.0

def test_security_supremacy_over_learning():
    lm = LearningManager()
    # Learned recommendation might prefer tool_z
    allowed_by_policy = ["tool_x", "tool_y"]
    assert lm.enforce_security_supremacy("tool_x", allowed_by_policy) is True
    assert lm.enforce_security_supremacy("tool_z", allowed_by_policy) is False

def test_user_deletes_learning_record():
    lm = LearningManager()
    user_id = "user_p53_del"
    rec = lm.record_execution(user_id=user_id, session_id="sess_1", task_type="research", outcome="success")
    record_id = rec["id"]

    assert lm.delete_learning_record(record_id, user_id) is True
    assert lm.delete_learning_record(record_id, user_id) is False  # Already deleted
