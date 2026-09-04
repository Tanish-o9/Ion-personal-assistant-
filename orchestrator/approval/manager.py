import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from database.connection import get_db_context
from database.models import ApprovalModel, utc_now_iso
from orchestrator.observability import jarvis_logger

class ApprovalManager:
    """
    Manages persistent human-in-the-loop approval requests, approval/rejection resolution,
    expiration cleanup, and multi-user isolation.
    """
    def create_approval(
        self,
        user_id: str,
        session_id: str,
        action_type: str,
        action_summary: str,
        risk_level: str = "medium",
        job_id: Optional[str] = None,
        expires_in_seconds: int = 3600,
    ) -> Dict[str, Any]:
        exp_time = (datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)).isoformat()
        with get_db_context() as db:
            appr = ApprovalModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                session_id=session_id,
                job_id=job_id,
                action_type=action_type,
                action_summary=action_summary,
                risk_level=risk_level,
                status="pending",
                expires_at=exp_time,
            )
            db.add(appr)
            db.commit()
            db.refresh(appr)
            jarvis_logger.info("Created approval request '%s' for user %s (Risk: %s)", appr.id, user_id, risk_level)
            return self._to_dict(appr)

    def list_approvals(self, user_id: str, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        self.check_expirations()
        with get_db_context() as db:
            query = db.query(ApprovalModel).filter(ApprovalModel.user_id == user_id)
            if status_filter:
                query = query.filter(ApprovalModel.status == status_filter)
            items = query.all()
            return [self._to_dict(item) for item in items]

    def get_approval(self, approval_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        self.check_expirations()
        with get_db_context() as db:
            appr = db.query(ApprovalModel).filter(ApprovalModel.id == approval_id, ApprovalModel.user_id == user_id).first()
            return self._to_dict(appr) if appr else None

    def approve(self, approval_id: str, user_id: str) -> bool:
        self.check_expirations()
        with get_db_context() as db:
            appr = db.query(ApprovalModel).filter(ApprovalModel.id == approval_id, ApprovalModel.user_id == user_id).first()
            if not appr or appr.status != "pending":
                return False

            appr.status = "approved"
            appr.resolved_at = utc_now_iso()
            appr.resolved_by = user_id
            db.commit()
            jarvis_logger.info("Approval '%s' approved by user %s", approval_id, user_id)
            return True

    def reject(self, approval_id: str, user_id: str) -> bool:
        self.check_expirations()
        with get_db_context() as db:
            appr = db.query(ApprovalModel).filter(ApprovalModel.id == approval_id, ApprovalModel.user_id == user_id).first()
            if not appr or appr.status != "pending":
                return False

            appr.status = "rejected"
            appr.resolved_at = utc_now_iso()
            appr.resolved_by = user_id
            db.commit()
            jarvis_logger.info("Approval '%s' rejected by user %s", approval_id, user_id)
            return True

    def check_expirations(self) -> None:
        now_iso = utc_now_iso()
        with get_db_context() as db:
            expired_items = db.query(ApprovalModel).filter(
                ApprovalModel.status == "pending",
                ApprovalModel.expires_at <= now_iso,
            ).all()

            for item in expired_items:
                item.status = "expired"
                item.resolved_at = now_iso

            if expired_items:
                db.commit()

    @staticmethod
    def _to_dict(appr: ApprovalModel) -> Dict[str, Any]:
        return {
            "id": appr.id,
            "user_id": appr.user_id,
            "session_id": appr.session_id,
            "job_id": appr.job_id,
            "action_type": appr.action_type,
            "action_summary": appr.action_summary,
            "risk_level": appr.risk_level,
            "status": appr.status,
            "created_at": appr.created_at,
            "expires_at": appr.expires_at,
            "resolved_at": appr.resolved_at,
            "resolved_by": appr.resolved_by,
        }

default_approval_manager = ApprovalManager()
