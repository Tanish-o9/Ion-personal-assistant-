import json
import uuid
from typing import Any, Dict, List, Optional
from database.connection import get_db_context
from database.models import LearningRecordModel, utc_now_iso
from orchestrator.learning.models import ToolPerformanceMetrics
from orchestrator.observability import jarvis_logger, default_metrics

class LearningManager:
    """
    Manages operational task execution records, user feedback, tool/skill performance statistics,
    and freshness decay signals. Strictly isolated from source code modification or prompt injection.
    """
    def record_execution(
        self,
        user_id: str,
        session_id: str,
        task_type: str,
        skill_used: Optional[str] = None,
        tools_used: Optional[List[str]] = None,
        outcome: str = "success",
        failure_reason: Optional[str] = None,
        latency_ms: float = 0.0,
        cost_usd: float = 0.0,
    ) -> Dict[str, Any]:
        tools_json = json.dumps(tools_used or [])
        with get_db_context() as db:
            rec = LearningRecordModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                session_id=session_id,
                task_type=task_type,
                skill_used=skill_used,
                tools_used=tools_json,
                outcome=outcome,
                failure_reason=failure_reason,
                latency_ms=latency_ms,
                cost_usd=cost_usd,
            )
            db.add(rec)
            db.commit()
            db.refresh(rec)
            default_metrics.record_learning(task_type=task_type, outcome=outcome)
            return self._to_dict(rec)

    def add_user_feedback(self, record_id: str, user_id: str, feedback: str, reason: Optional[str] = None) -> bool:
        with get_db_context() as db:
            rec = db.query(LearningRecordModel).filter(LearningRecordModel.id == record_id, LearningRecordModel.user_id == user_id).first()
            if not rec:
                return False
            rec.user_feedback = feedback
            rec.feedback_reason = reason
            db.commit()
            return True

    def get_tool_performance(self, tool_name: str, user_id: str) -> ToolPerformanceMetrics:
        with get_db_context() as db:
            records = db.query(LearningRecordModel).filter(LearningRecordModel.user_id == user_id).all()
            matching = [r for r in records if tool_name in json.loads(r.tools_used or "[]")]
            if not matching:
                return ToolPerformanceMetrics(tool_name=tool_name, total_executions=0, success_rate=1.0)

            total = len(matching)
            successes = sum(1 for r in matching if r.outcome == "success")
            failures = total - successes
            avg_lat = sum(r.latency_ms for r in matching) / total if total > 0 else 0.0
            succ_rate = (successes / total) if total > 0 else 1.0

            return ToolPerformanceMetrics(
                tool_name=tool_name,
                total_executions=total,
                successes=successes,
                failures=failures,
                success_rate=round(succ_rate, 2),
                average_latency_ms=round(avg_lat, 2),
            )

    def get_workflow_reliability(self, task_type: str, user_id: str) -> Dict[str, Any]:
        """Calculates workflow pattern reliability scores for skills and tools for a specific task type."""
        with get_db_context() as db:
            records = db.query(LearningRecordModel).filter(
                LearningRecordModel.user_id == user_id,
                LearningRecordModel.task_type == task_type
            ).all()

            if not records:
                return {"task_type": task_type, "recommended_skill": None, "tool_scores": {}, "confidence": 0.0}

            skill_counts: Dict[str, Dict[str, int]] = {}
            tool_counts: Dict[str, Dict[str, int]] = {}

            for r in records:
                # Skill counting
                if r.skill_used:
                    sk = r.skill_used
                    if sk not in skill_counts:
                        skill_counts[sk] = {"success": 0, "total": 0}
                    skill_counts[sk]["total"] += 1
                    if r.outcome == "success":
                        skill_counts[sk]["success"] += 1

                # Tool counting
                tools = json.loads(r.tools_used or "[]")
                for t in tools:
                    if t not in tool_counts:
                        tool_counts[t] = {"success": 0, "total": 0}
                    tool_counts[t]["total"] += 1
                    if r.outcome == "success":
                        tool_counts[t]["success"] += 1

            best_skill = None
            highest_skill_rate = -1.0
            for sk, stats in skill_counts.items():
                rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
                if rate > highest_skill_rate:
                    highest_skill_rate = rate
                    best_skill = sk

            tool_scores = {
                t: round(stats["success"] / stats["total"], 2)
                for t, stats in tool_counts.items() if stats["total"] > 0
            }

            return {
                "task_type": task_type,
                "recommended_skill": best_skill,
                "tool_scores": tool_scores,
                "confidence": min(len(records) / 10.0, 1.0)
            }

    @staticmethod
    def enforce_security_supremacy(tool_name: str, allowed_tools_by_policy: List[str]) -> bool:
        """Security Policy ALWAYS overrides learned recommendations."""
        return tool_name in allowed_tools_by_policy

    def clear_user_learning_data(self, user_id: str) -> int:
        with get_db_context() as db:
            count = db.query(LearningRecordModel).filter(LearningRecordModel.user_id == user_id).delete()
            db.commit()
            return count

    def delete_learning_record(self, record_id: str, user_id: str) -> bool:
        with get_db_context() as db:
            count = db.query(LearningRecordModel).filter(
                LearningRecordModel.id == record_id,
                LearningRecordModel.user_id == user_id
            ).delete()
            db.commit()
            return count > 0


    @staticmethod
    def _to_dict(rec: LearningRecordModel) -> Dict[str, Any]:
        return {
            "id": rec.id,
            "user_id": rec.user_id,
            "session_id": rec.session_id,
            "task_type": rec.task_type,
            "skill_used": rec.skill_used,
            "tools_used": json.loads(rec.tools_used or "[]"),
            "outcome": rec.outcome,
            "failure_reason": rec.failure_reason,
            "latency_ms": rec.latency_ms,
            "cost_usd": rec.cost_usd,
            "user_feedback": rec.user_feedback,
            "created_at": rec.created_at,
        }

default_learning_manager = LearningManager()

