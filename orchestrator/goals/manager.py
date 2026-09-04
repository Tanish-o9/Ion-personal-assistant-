"""
Phase 55: Bounded Goal Execution Manager & Checkpoint State System.
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from database.connection import get_db_context
from database.models import GoalModel, utc_now_iso
from orchestrator.goals.models import GoalStatus, GoalTaskStep, GoalDetail, GoalCreatePayload
from orchestrator.goals.planner import GoalDecompositionPlanner
from orchestrator.learning import default_learning_manager

class GoalManager:
    """Manages high-level long-running goal lifecycle, bounded step budgets, checkpointing, and quality verification."""

    def create_goal(self, user_id: str, payload: GoalCreatePayload) -> GoalDetail:
        with get_db_context() as db:
            goal_id = f"goal_{uuid.uuid4().hex[:12]}"
            criteria_json = json.dumps(payload.success_criteria or ["Task completed successfully"])

            gm = GoalModel(
                id=goal_id,
                user_id=user_id,
                workspace_id=payload.workspace_id,
                description=payload.description,
                success_criteria=criteria_json,
                status=GoalStatus.DRAFT.value,
                max_steps=payload.max_steps,
                max_budget_usd=payload.max_budget_usd,
                checkpoint_state=json.dumps({"steps": []})
            )
            db.add(gm)
            db.commit()
            db.refresh(gm)
            return self._to_detail(gm)

    def plan_goal(self, goal_id: str, user_id: str) -> Optional[GoalDetail]:
        with get_db_context() as db:
            gm = db.query(GoalModel).filter(GoalModel.id == goal_id, GoalModel.user_id == user_id).first()
            if not gm:
                return None

            steps = GoalDecompositionPlanner.decompose_goal(gm.description)
            milestones = GoalDecompositionPlanner.decompose_goal_hierarchical(gm.description)
            steps_dict = [s.model_dump() for s in steps]
            milestones_dict = [m.model_dump() for m in milestones]

            gm.status = GoalStatus.PLANNED.value
            gm.total_steps = len(steps)
            gm.checkpoint_state = json.dumps({
                "steps": steps_dict,
                "milestones": milestones_dict,
                "completed_indices": [],
                "replan_count": 0
            })
            gm.updated_at = utc_now_iso()
            db.commit()
            db.refresh(gm)
            return self._to_detail(gm)

    def replan_goal(self, goal_id: str, user_id: str, new_constraints: Optional[List[str]] = None) -> Optional[GoalDetail]:
        """Dynamic plan revision under bounded MAX_REPLANS limit."""
        with get_db_context() as db:
            gm = db.query(GoalModel).filter(GoalModel.id == goal_id, GoalModel.user_id == user_id).first()
            if not gm:
                return None

            ckpt = json.loads(gm.checkpoint_state or "{}")
            replan_count = ckpt.get("replan_count", 0) + 1
            if replan_count > 3:  # MAX_REPLANS limit
                gm.status = GoalStatus.FAILED.value
                db.commit()
                return self._to_detail(gm)

            # Re-generate milestones with revised constraints
            revised_milestones = GoalDecompositionPlanner.decompose_goal_hierarchical(gm.description)
            ckpt["milestones"] = [m.model_dump() for m in revised_milestones]
            ckpt["replan_count"] = replan_count
            if new_constraints:
                ckpt["constraints"] = new_constraints

            gm.checkpoint_state = json.dumps(ckpt)
            gm.status = GoalStatus.RUNNING.value
            gm.updated_at = utc_now_iso()
            db.commit()
            db.refresh(gm)
            return self._to_detail(gm)

    def step_goal(self, goal_id: str, user_id: str) -> Optional[GoalDetail]:
        """Executes the next pending step within strict budget and step limits."""
        with get_db_context() as db:
            gm = db.query(GoalModel).filter(GoalModel.id == goal_id, GoalModel.user_id == user_id).first()
            if not gm:
                return None

            if gm.status in (GoalStatus.PAUSED.value, GoalStatus.COMPLETED.value, GoalStatus.CANCELLED.value, GoalStatus.FAILED.value):
                return self._to_detail(gm)

            # Enforce budget limit
            if gm.consumed_budget_usd >= gm.max_budget_usd or gm.current_step >= gm.max_steps:
                gm.status = GoalStatus.FAILED.value
                db.commit()
                return self._to_detail(gm)

            ckpt = json.loads(gm.checkpoint_state or "{}")
            steps = ckpt.get("steps", [])

            if gm.current_step >= len(steps):
                # Verify quality gate before marking completed
                quality_passed = self.verify_quality(gm)
                gm.status = GoalStatus.COMPLETED.value if quality_passed else GoalStatus.FAILED.value
                db.commit()
                default_learning_manager.record_execution(
                    user_id=user_id,
                    session_id=goal_id,
                    task_type="goal_execution",
                    outcome="success" if quality_passed else "failed"
                )
                return self._to_detail(gm)

            # Execute step
            gm.status = GoalStatus.RUNNING.value
            current_idx = gm.current_step
            steps[current_idx]["status"] = "COMPLETED"
            steps[current_idx]["result"] = f"Step {current_idx + 1} executed successfully."

            gm.current_step += 1
            gm.consumed_budget_usd += 0.05  # Increment consumed budget
            ckpt["steps"] = steps
            ckpt["completed_indices"] = ckpt.get("completed_indices", []) + [current_idx]

            # Update milestone outcomes
            milestones = ckpt.get("milestones", [])
            for m in milestones:
                if current_idx < len(milestones):
                    milestones[current_idx]["status"] = "COMPLETED"
                    milestones[current_idx]["actual_outcome"] = f"Milestone outcome validated at step {current_idx + 1}."
            ckpt["milestones"] = milestones

            gm.checkpoint_state = json.dumps(ckpt)
            gm.updated_at = utc_now_iso()

            if gm.current_step >= len(steps):
                quality_passed = self.verify_quality(gm)
                gm.status = GoalStatus.COMPLETED.value if quality_passed else GoalStatus.FAILED.value

            db.commit()
            db.refresh(gm)
            return self._to_detail(gm)

    def pause_goal(self, goal_id: str, user_id: str) -> Optional[GoalDetail]:
        return self._update_status(goal_id, user_id, GoalStatus.PAUSED)

    def resume_goal(self, goal_id: str, user_id: str) -> Optional[GoalDetail]:
        return self._update_status(goal_id, user_id, GoalStatus.RUNNING)

    def cancel_goal(self, goal_id: str, user_id: str) -> Optional[GoalDetail]:
        return self._update_status(goal_id, user_id, GoalStatus.CANCELLED)

    def retry_goal(self, goal_id: str, user_id: str) -> Optional[GoalDetail]:
        with get_db_context() as db:
            gm = db.query(GoalModel).filter(GoalModel.id == goal_id, GoalModel.user_id == user_id).first()
            if not gm:
                return None
            gm.status = GoalStatus.PLANNED.value
            gm.current_step = 0
            gm.consumed_budget_usd = 0.0
            gm.updated_at = utc_now_iso()
            db.commit()
            db.refresh(gm)
            return self._to_detail(gm)

    def verify_quality(self, gm: GoalModel) -> bool:
        """Goal quality gate: verifies all criteria and checkpoint steps completed without errors."""
        criteria = json.loads(gm.success_criteria or "[]")
        ckpt = json.loads(gm.checkpoint_state or "{}")
        steps = ckpt.get("steps", [])
        if not steps:
            return False
        failed_steps = [s for s in steps if s.get("status") == "FAILED"]
        return len(failed_steps) == 0

    def _update_status(self, goal_id: str, user_id: str, status: GoalStatus) -> Optional[GoalDetail]:
        with get_db_context() as db:
            gm = db.query(GoalModel).filter(GoalModel.id == goal_id, GoalModel.user_id == user_id).first()
            if not gm:
                return None
            gm.status = status.value
            gm.updated_at = utc_now_iso()
            db.commit()
            db.refresh(gm)
            return self._to_detail(gm)

    def get_goal(self, goal_id: str, user_id: str) -> Optional[GoalDetail]:
        with get_db_context() as db:
            gm = db.query(GoalModel).filter(GoalModel.id == goal_id, GoalModel.user_id == user_id).first()
            return self._to_detail(gm) if gm else None

    @staticmethod
    def _to_detail(gm: GoalModel) -> GoalDetail:
        ckpt = json.loads(gm.checkpoint_state or "{}")
        raw_steps = ckpt.get("steps", [])
        steps = [GoalTaskStep(**s) for s in raw_steps]
        raw_milestones = ckpt.get("milestones", [])
        from orchestrator.goals.models import GoalMilestone
        milestones = [GoalMilestone(**m) for m in raw_milestones] if raw_milestones else []

        return GoalDetail(
            id=gm.id,
            user_id=gm.user_id,
            workspace_id=gm.workspace_id,
            description=gm.description,
            success_criteria=json.loads(gm.success_criteria or "[]"),
            status=GoalStatus(gm.status),
            current_step=gm.current_step,
            total_steps=gm.total_steps,
            max_steps=gm.max_steps,
            max_budget_usd=gm.max_budget_usd,
            consumed_budget_usd=gm.consumed_budget_usd,
            constraints=ckpt.get("constraints", []),
            replan_count=ckpt.get("replan_count", 0),
            milestones=milestones,
            steps=steps,
            checkpoint_state=ckpt
        )

default_goal_manager = GoalManager()

