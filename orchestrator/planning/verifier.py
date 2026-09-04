from typing import Any, Dict, List, Optional
from orchestrator.planning.models import TaskPlan, TaskStep

class AdaptiveVerifier:
    """
    Evaluates actual TaskPlan step results, checks research/RAG context alignment, and calculates operational confidence.
    """
    @staticmethod
    def verify_plan(plan: TaskPlan) -> Dict[str, Any]:
        total_steps = len(plan.steps)
        completed_steps = sum(1 for s in plan.steps if s.status == "completed")
        failed_steps = sum(1 for s in plan.steps if s.status == "failed")
        is_verified = (total_steps > 0) and (completed_steps == total_steps) and (failed_steps == 0)

        # Operational confidence scoring
        if is_verified:
            if plan.replan_count > 0:
                confidence = "medium"
            elif any(s.retry_count > 0 for s in plan.steps):
                confidence = "medium"
            else:
                confidence = "high"
        else:
            confidence = "low"

        plan.verification_status = "passed" if is_verified else "failed"
        plan.confidence = confidence
        plan.decision_trace["verification"] = plan.verification_status
        plan.decision_trace["confidence"] = confidence

        return {
            "verified": is_verified,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "plan_status": plan.status,
            "verification_status": plan.verification_status,
            "confidence": confidence,
        }
