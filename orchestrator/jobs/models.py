import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

class Job:
    """
    Represents an asynchronous background execution job.
    """
    def __init__(
        self,
        user_id: str,
        session_id: str,
        job_type: str,
        id: Optional[str] = None,
        status: str = "pending",
        progress: int = 0,
        result: Optional[str] = None,
        error: Optional[str] = None,
        created_at: Optional[str] = None,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None,
    ):
        if not user_id or not isinstance(user_id, str):
            raise ValueError("user_id must be a non-empty string.")
        if not session_id or not isinstance(session_id, str):
            raise ValueError("session_id must be a non-empty string.")

        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.session_id = session_id
        self.job_type = job_type
        self.status = status  # pending, running, completed, failed, cancelled
        self.progress = max(0, min(100, progress))
        self.result = result
        self.error = error
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.started_at = started_at
        self.completed_at = completed_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "job_type": self.job_type,
            "status": self.status,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }
