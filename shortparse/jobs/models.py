from datetime import datetime
from datetime import timezone
from enum import Enum
from uuid import uuid4


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


def utc_now_iso() -> str:
    return datetime.now(
        timezone.utc,
    ).isoformat()


def create_job(
    report_url: str,
    report_code: str,
) -> dict:
    now = utc_now_iso()

    return {
        "job_id": str(uuid4()),
        "status": JobStatus.QUEUED.value,
        "report_url": report_url,
        "report_code": report_code,
        "created_at": now,
        "updated_at": now,
        "result_path": None,
        "error": None,

        # Live status console fields
        "progress": 0,
        "current_step": "Queued",
        "logs": [
            {
                "time": now,
                "level": "info",
                "message": "Report submitted.",
            }
        ],
    }


def update_job_status(
    job: dict,
    status: JobStatus,
    result_path: str | None = None,
    error: str | None = None,
) -> dict:
    job["status"] = status.value
    job["updated_at"] = utc_now_iso()

    if result_path is not None:
        job["result_path"] = result_path

    if error is not None:
        job["error"] = error

    return job

def add_job_log(
    job: dict,
    message: str,
    level: str = "info",
    progress: int | None = None,
    current_step: str | None = None,
) -> dict:
    job["updated_at"] = utc_now_iso()

    if "logs" not in job:
        job["logs"] = []

    job["logs"].append(
        {
            "time": job["updated_at"],
            "level": level,
            "message": message,
        }
    )

    if progress is not None:
        job["progress"] = max(0, min(100, progress))

    if current_step is not None:
        job["current_step"] = current_step

    return job