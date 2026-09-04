import pytest
from orchestrator.learning import default_learning_manager

def test_learning_record_and_feedback():
    user_id = "user_learn_1"
    session_id = "sess_learn_1"

    rec = default_learning_manager.record_execution(
        user_id=user_id,
        session_id=session_id,
        task_type="research",
        skill_used="research_skill",
        tools_used=["web_search", "web_fetch"],
        outcome="success",
        latency_ms=120.0,
    )
    assert rec["outcome"] == "success"
    assert rec["task_type"] == "research"

    # Add feedback
    assert default_learning_manager.add_user_feedback(rec["id"], user_id, "positive", "Great summary!") is True

def test_tool_performance_metrics():
    user_id = "user_learn_2"
    session_id = "sess_learn_2"

    default_learning_manager.record_execution(user_id=user_id, session_id=session_id, task_type="calc", tools_used=["calculator"], outcome="success", latency_ms=10.0)
    default_learning_manager.record_execution(user_id=user_id, session_id=session_id, task_type="calc", tools_used=["calculator"], outcome="failed", latency_ms=20.0)

    perf = default_learning_manager.get_tool_performance("calculator", user_id)
    assert perf.total_executions == 2
    assert perf.successes == 1
    assert perf.failures == 1
    assert perf.success_rate == 0.5

def test_learning_data_cleanup():
    user_id = "user_learn_3"
    default_learning_manager.record_execution(user_id=user_id, session_id="s3", task_type="chat", outcome="success")
    deleted = default_learning_manager.clear_user_learning_data(user_id)
    assert deleted >= 1
