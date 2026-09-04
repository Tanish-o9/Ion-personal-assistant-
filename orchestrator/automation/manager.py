import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from database.connection import get_db_context
from database.models import AutomationModel, AutomationExecutionModel, utc_now_iso
from orchestrator.jobs import default_job_manager
from orchestrator.observability import jarvis_logger

class AutomationManager:
    """
    Manages workflow automation schedules, execution history, user ownership isolation,
    and background job queue dispatching.
    """
    def create_automation(self, user_id: str, name: str, workflow_text: str, description: Optional[str] = None, schedule_cron: str = "0 9 * * 1", tz: str = "UTC") -> Dict[str, Any]:
        with get_db_context() as db:
            auto = AutomationModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                name=name,
                description=description,
                workflow_text=workflow_text,
                schedule_cron=schedule_cron,
                timezone=tz,
                enabled=True,
                next_run_at=utc_now_iso(),
            )
            db.add(auto)
            db.commit()
            db.refresh(auto)
            return self._to_dict(auto)

    def list_automations(self, user_id: str) -> List[Dict[str, Any]]:
        with get_db_context() as db:
            items = db.query(AutomationModel).filter(AutomationModel.user_id == user_id).all()
            return [self._to_dict(item) for item in items]

    def get_automation(self, automation_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        with get_db_context() as db:
            auto = db.query(AutomationModel).filter(AutomationModel.id == automation_id, AutomationModel.user_id == user_id).first()
            return self._to_dict(auto) if auto else None

    def pause_automation(self, automation_id: str, user_id: str) -> bool:
        with get_db_context() as db:
            auto = db.query(AutomationModel).filter(AutomationModel.id == automation_id, AutomationModel.user_id == user_id).first()
            if not auto:
                return False
            auto.enabled = False
            auto.updated_at = utc_now_iso()
            db.commit()
            return True

    def resume_automation(self, automation_id: str, user_id: str) -> bool:
        with get_db_context() as db:
            auto = db.query(AutomationModel).filter(AutomationModel.id == automation_id, AutomationModel.user_id == user_id).first()
            if not auto:
                return False
            auto.enabled = True
            auto.updated_at = utc_now_iso()
            db.commit()
            return True

    def run_automation(self, automation_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Manually triggers a scheduled automation by submitting a background job to Phase 16 JobQueue.
        """
        with get_db_context() as db:
            auto = db.query(AutomationModel).filter(AutomationModel.id == automation_id, AutomationModel.user_id == user_id).first()
            if not auto or not auto.enabled:
                return None

            # Create background job via Phase 16 JobManager
            job = default_job_manager.submit_job(
                user_id=user_id,
                session_id=f"auto-session-{auto.id[:8]}",
                job_type="long_task",
                payload_data=auto.workflow_text,
            )

            # Record execution history item
            exec_item = AutomationExecutionModel(
                id=str(uuid.uuid4()),
                automation_id=auto.id,
                job_id=job.id,
                status="running",
                approval_status="approved",
                started_at=utc_now_iso(),
            )
            auto.last_run_at = utc_now_iso()
            db.add(exec_item)
            db.commit()

            return {
                "execution_id": exec_item.id,
                "automation_id": auto.id,
                "job_id": job.id,
                "status": "running",
            }

    def delete_automation(self, automation_id: str, user_id: str) -> bool:
        with get_db_context() as db:
            auto = db.query(AutomationModel).filter(AutomationModel.id == automation_id, AutomationModel.user_id == user_id).first()
            if not auto:
                return False
            db.delete(auto)
            db.commit()
            return True

    @staticmethod
    def _to_dict(auto: AutomationModel) -> Dict[str, Any]:
        return {
            "id": auto.id,
            "user_id": auto.user_id,
            "name": auto.name,
            "description": auto.description,
            "workflow_text": auto.workflow_text,
            "schedule_cron": auto.schedule_cron,
            "timezone": auto.timezone,
            "enabled": auto.enabled,
            "next_run_at": auto.next_run_at,
            "last_run_at": auto.last_run_at,
            "created_at": auto.created_at,
        }

default_automation_manager = AutomationManager()
