import asyncio
import logging
from typing import Dict, List, Optional, Set

from orchestrator.jobs.models import Job
from orchestrator.jobs.handlers import JOB_HANDLERS
from database.repository import JobRepository
from orchestrator.observability import default_metrics, jarvis_logger

logger = logging.getLogger(__name__)

MAX_JOB_RETRIES = 2

class JobManager:
    """
    Manages background job creation, async worker task execution, progress updates, bounded retries, and cancellation.
    Instrumented with background job metrics and status tracking.
    """
    def __init__(self, max_retries: int = MAX_JOB_RETRIES):
        self.max_retries = max_retries
        self._cancelled_jobs: Set[str] = set()
        self._running_tasks: Dict[str, asyncio.Task] = {}

    def submit_job(self, user_id: str, session_id: str, job_type: str, payload_data: str = "") -> Job:
        """
        Creates and persists a job record, then launches the background async worker task.
        """
        db_job = JobRepository.create_job(user_id=user_id, session_id=session_id, job_type=job_type)
        if payload_data:
            JobRepository.update_job(db_job.id, result=payload_data)

        job = Job(
            id=db_job.id,
            user_id=db_job.user_id,
            session_id=db_job.session_id,
            job_type=db_job.job_type,
            status=db_job.status,
            progress=db_job.progress,
            result=payload_data,
        )

        default_metrics.record_job(job_type=job_type, status="created")

        # Safely create task if event loop is running
        try:
            loop = asyncio.get_running_loop()
            task = loop.create_task(self._run_job_worker(job))
            self._running_tasks[job.id] = task
        except RuntimeError:
            pass

        return job

    def cancel_job(self, job_id: str, user_id: str) -> bool:
        """
        Cancels a background job if owned by user_id.
        """
        job_db = JobRepository.get_job(job_id)
        if not job_db or job_db.user_id != user_id:
            return False

        self._cancelled_jobs.add(job_id)
        JobRepository.update_job(job_id, status="cancelled", error="Job cancelled by user.")
        default_metrics.record_job(job_type=job_db.job_type, status="cancelled")

        if job_id in self._running_tasks:
            self._running_tasks[job_id].cancel()

        return True

    def get_job(self, job_id: str, user_id: str) -> Optional[Job]:
        """
        Retrieves a job by ID enforcing user isolation ownership.
        """
        job_db = JobRepository.get_job(job_id)
        if not job_db or job_db.user_id != user_id:
            return None

        return Job(
            id=job_db.id,
            user_id=job_db.user_id,
            session_id=job_db.session_id,
            job_type=job_db.job_type,
            status=job_db.status,
            progress=job_db.progress,
            result=job_db.result,
            error=job_db.error,
            created_at=job_db.created_at,
            started_at=job_db.started_at,
            completed_at=job_db.completed_at,
        )

    def get_user_jobs(self, user_id: str) -> List[Job]:
        """
        Retrieves all jobs for an authenticated user.
        """
        db_jobs = JobRepository.get_user_jobs(user_id)
        return [
            Job(
                id=j.id,
                user_id=j.user_id,
                session_id=j.session_id,
                job_type=j.job_type,
                status=j.status,
                progress=j.progress,
                result=j.result,
                error=j.error,
                created_at=j.created_at,
                started_at=j.started_at,
                completed_at=j.completed_at,
            )
            for j in db_jobs
        ]

    async def _run_job_worker(self, job: Job) -> None:
        """
        Worker task executing job handler with retry resilience.
        """
        handler = JOB_HANDLERS.get(job.job_type)
        if not handler:
            JobRepository.update_job(job.id, status="failed", error=f"Unknown job_type '{job.job_type}'")
            default_metrics.record_job(job_type=job.job_type, status="failed")
            return

        JobRepository.update_job(job.id, status="running", progress=5)

        def update_progress(prog: int, msg: str) -> None:
            if job.id not in self._cancelled_jobs:
                JobRepository.update_job(job.id, progress=prog)

        attempts = 0
        last_exception = None

        while attempts <= self.max_retries:
            if job.id in self._cancelled_jobs:
                JobRepository.update_job(job.id, status="cancelled")
                default_metrics.record_job(job_type=job.job_type, status="cancelled")
                return

            try:
                result_text = await handler.execute(job, update_progress)
                if job.id not in self._cancelled_jobs:
                    JobRepository.update_job(job.id, status="completed", progress=100, result=result_text)
                    default_metrics.record_job(job_type=job.job_type, status="completed")
                return
            except asyncio.CancelledError:
                JobRepository.update_job(job.id, status="cancelled", error="Worker task cancelled.")
                default_metrics.record_job(job_type=job.job_type, status="cancelled")
                return
            except Exception as exc:
                attempts += 1
                last_exception = exc
                jarvis_logger.warning("Job %s attempt %d failed: %s", job.id, attempts, exc)
                if attempts <= self.max_retries:
                    await asyncio.sleep(0.2)

        JobRepository.update_job(job.id, status="failed", error=str(last_exception))
        default_metrics.record_job(job_type=job.job_type, status="failed")
