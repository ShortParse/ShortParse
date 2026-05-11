from shortparse.jobs.models import JobStatus
from shortparse.jobs.models import add_job_log
from shortparse.jobs.models import update_job_status

JOBS: dict[str, dict] = {}


def save_job(job: dict) -> dict:
    JOBS[job["job_id"]] = job
    return job


def get_job(job_id: str) -> dict | None:
    return JOBS.get(job_id)


def list_jobs() -> list[dict]:
    return list(JOBS.values())


def mark_job_running(job_id: str) -> dict | None:
    job = get_job(job_id)

    if not job:
        return None

    return update_job_status(
        job,
        JobStatus.RUNNING,
    )


def mark_job_completed(
    job_id: str,
    result_path: str | None = None,
) -> dict | None:
    job = get_job(job_id)

    if not job:
        return None

    return update_job_status(
        job,
        JobStatus.COMPLETED,
        result_path=result_path,
    )


def mark_job_failed(
    job_id: str,
    error: str,
) -> dict | None:
    job = get_job(job_id)

    if not job:
        return None

    return update_job_status(
        job,
        JobStatus.FAILED,
        error=error,
    )

def append_job_log(
    job_id: str,
    message: str,
    level: str = "info",
    progress: int | None = None,
    current_step: str | None = None,
) -> dict | None:
    job = get_job(job_id)

    if not job:
        return None

    return add_job_log(
        job,
        message,
        level=level,
        progress=progress,
        current_step=current_step,
    )