"""
Unit Tests for Phase 62: Agent Runtime 2.0.
"""

import pytest
from orchestrator.agents.runtime import (
    AgentRuntime,
    AgentState,
)

def test_agent_spawning_concurrency_and_execution():
    runtime = AgentRuntime(max_concurrency=2)
    user_id = "user_agent_1"

    a1 = runtime.spawn_agent(user_id, "research_agent")
    a2 = runtime.spawn_agent(user_id, "coding_agent")
    a3 = runtime.spawn_agent(user_id, "docs_agent") # Queued due to concurrency limit = 2

    assert a1.state == AgentState.CREATED
    assert a2.state == AgentState.CREATED
    assert a3.state == AgentState.QUEUED

    res = runtime.assign_and_run_task(a1.agent_id, "task_001")
    assert res.status == AgentState.COMPLETED
    assert res.execution_time_ms > 0

def test_agent_message_and_checkpoint_recovery():
    runtime = AgentRuntime()
    a1 = runtime.spawn_agent("u1", "agent_a")
    a2 = runtime.spawn_agent("u1", "agent_b")

    msg = runtime.send_agent_message(a1.agent_id, a2.agent_id, "Requesting research evidence")
    assert msg.recipient_agent_id == a2.agent_id

    runtime.assign_and_run_task(a1.agent_id, "task_checkpoint_test")
    recovered = runtime.recover_agent_from_checkpoint(a1.agent_id)
    assert recovered is not None
    assert recovered.state == AgentState.RUNNING

def test_agent_cancellation():
    runtime = AgentRuntime()
    a1 = runtime.spawn_agent("u1", "agent_c")
    assert runtime.cancel_agent(a1.agent_id) is True
    assert a1.state == AgentState.CANCELLED
