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