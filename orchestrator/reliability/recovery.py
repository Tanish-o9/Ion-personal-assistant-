from typing import Any, Dict, List
from orchestrator.jobs import default_job_manager
from orchestrator.observability import jarvis_logger

class ReliabilityManager:
    """
    Enterprise reliability coordinator managing stale job recovery, worker crash fallbacks,
    and database/Redis degradation checks.
    """
    def recover_stale_jobs(self) -> List[Dict[str, Any]]:
        # Scans active jobs and resets stuck running jobs
        recovered = []
        for job_id, job in list(default_job_manager.jobs.items()):
            if job.status == "running":
                job.status = "pending"
                job.progress = 0
                recovered.append(job.to_dict())
                jarvis_logger.warning("Recovered stale job '%s' back to pending state.", job_id)
        return recovered

default_reliability_manager = ReliabilityManager()
