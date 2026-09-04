"""
Unit & Integration Tests for Phase 55: JARVIS 2.0 Bounded Autonomous Intelligence Platform.
"""

import pytest
from database.connection import init_db
from orchestrator.goals import (
    GoalManager,
    GoalCreatePayload,
    GoalStatus,
    GoalDecompositionPlanner,
)

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def test_goal_decomposition_planner():
    steps = GoalDecompositionPlanner.decompose_goal("Build a python microservice for analytics")
    assert len(steps) == 3
    assert steps[0].agent_type == "research"
    assert steps[1].agent_type == "coding"
    assert steps[2].agent_type == "verification"

def test_goal_lifecycle_creation_planning_execution():
    gm = GoalManager()
    user_id = "user_goal_test"
    payload = GoalCreatePayload(
        description="Research market trends and create report",
        success_criteria=["Report written", "Data verified"],
        max_steps=5,
        max_budget_usd=1.0
    )

    # 1. Create DRAFT Goal
    goal = gm.create_goal(user_id=user_id, payload=payload)
    assert goal.status == GoalStatus.DRAFT
    assert goal.id.startswith("goal_")

    # 2. Plan Goal
    planned = gm.plan_goal(goal.id, user_id)
    assert planned.status == GoalStatus.PLANNED
    assert planned.total_steps == 3

    # 3. Step Goal (Executes step 1)
    step1 = gm.step_goal(goal.id, user_id)
    assert step1.status == GoalStatus.RUNNING
    assert step1.current_step == 1
    assert step1.consumed_budget_usd > 0

    # 4. Step Goal (Step 2)
    step2 = gm.step_goal(goal.id, user_id)
    assert step2.current_step == 2

    # 5. Step Goal (Step 3 -> Quality gate -> COMPLETED)
    completed = gm.step_goal(goal.id, user_id)
    assert completed.status == GoalStatus.COMPLETED
    assert completed.current_step == 3

def test_goal_pause_resume_cancel():
    gm = GoalManager()
    user_id = "user_goal_pause"
    goal = gm.create_goal(user_id=user_id, payload=GoalCreatePayload(description="Test pause resume"))
    gm.plan_goal(goal.id, user_id)

    paused = gm.pause_goal(goal.id, user_id)
    assert paused.status == GoalStatus.PAUSED

    resumed = gm.resume_goal(goal.id, user_id)
    assert resumed.status == GoalStatus.RUNNING

    cancelled = gm.cancel_goal(goal.id, user_id)
    assert cancelled.status == GoalStatus.CANCELLED
