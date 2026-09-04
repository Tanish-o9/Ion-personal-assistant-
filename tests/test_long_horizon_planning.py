"""
Phase 81: Long-Horizon Planning Engine Tests.
"""

import pytest
from orchestrator.goals.models import GoalCreatePayload, GoalStatus, GoalHorizonLimits
from orchestrator.goals.planner import GoalDecompositionPlanner
from orchestrator.goals.manager import default_goal_manager
from database.connection import get_db_context
from database.models import UserModel

@pytest.fixture(autouse=True)
def setup_test_user():
    with get_db_context() as db:
        user = db.query(UserModel).filter_by(id="test_lh_user").first()
        if not user:
            user = UserModel(id="test_lh_user", username="lh_user", password_hash="hash")
            db.add(user)
            db.commit()

def test_hierarchical_decomposition():
    milestones = GoalDecompositionPlanner.decompose_goal_hierarchical("Build a scalable web microservice with authentication")
    assert len(milestones) == 3
    assert milestones[0].title.startswith("Milestone 1")
    assert len(milestones[0].tasks) > 0
    assert milestones[1].tasks[0].dependencies == ["t1"]
    assert milestones[1].tasks[0].can_parallel is True

def test_long_horizon_goal_lifecycle():
    payload = GoalCreatePayload(
        description="Migrate platform database to PostgreSQL HA cluster",
        success_criteria=["Zero data loss", "Latency under 50ms"],
        constraints=["No downtime during peak hours"],
        priority="HIGH",
        risk_tolerance="LOW",
        max_steps=10,
        max_budget_usd=2.0
    )
    goal = default_goal_manager.create_goal(user_id="test_lh_user", payload=payload)
    assert goal.id.startswith("goal_")
    assert goal.status == GoalStatus.DRAFT

    planned_goal = default_goal_manager.plan_goal(goal.id, user_id="test_lh_user")
    assert planned_goal.status == GoalStatus.PLANNED
    assert len(planned_goal.milestones) == 3

    stepped_goal = default_goal_manager.step_goal(goal.id, user_id="test_lh_user")
    assert stepped_goal.status == GoalStatus.RUNNING
    assert stepped_goal.current_step == 1

def test_replanning_and_horizon_limits():
    payload = GoalCreatePayload(
        description="Automate data pipeline processing",
        max_steps=5
    )
    goal = default_goal_manager.create_goal(user_id="test_lh_user", payload=payload)
    default_goal_manager.plan_goal(goal.id, user_id="test_lh_user")

    # Perform replans
    g1 = default_goal_manager.replan_goal(goal.id, user_id="test_lh_user", new_constraints=["Requires SSL encryption"])
    assert g1.replan_count == 1
    assert "Requires SSL encryption" in g1.constraints

    g2 = default_goal_manager.replan_goal(goal.id, user_id="test_lh_user")
    g3 = default_goal_manager.replan_goal(goal.id, user_id="test_lh_user")
    assert g3.replan_count == 3

    # 4th replan exceeds MAX_REPLANS (3)
    g4 = default_goal_manager.replan_goal(goal.id, user_id="test_lh_user")
    assert g4.status == GoalStatus.FAILED
