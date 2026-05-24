from dotenv import load_dotenv

load_dotenv()

import json
from pathlib import Path

from fastapi import BackgroundTasks
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from pydantic import BaseModel

from shortparse.client import WarcraftLogsClient
from shortparse.jobs.models import create_job
from shortparse.jobs.runner import run_analysis_job
from shortparse.jobs.store import (
    get_job,
    list_jobs,
    save_job,
)
from shortparse.logging import get_logger
from shortparse.report_parser import extract_report_code
from shortparse.reports.analysis import build_fight_analysis
from shortparse.reports.serializers import serialize_analysis
from shortparse.selector import select_best_boss_encounters
from shortparse.settings import (
    APP_NAME,
    APP_VERSION,
    ENVIRONMENT,
    has_warcraftlogs_credentials,
    JWT_SECRET_KEY,
    JWT_EXPIRATION_HOURS,
)
from starlette.middleware.sessions import SessionMiddleware
from shortparse.server.oauth import router as oauth_router

logger = get_logger(__name__)

app = FastAPI(
    title="ShortParse API",
    version=APP_VERSION,
)

# Enable signed session cookies for authentication
app.add_middleware(
    SessionMiddleware,
    secret_key=JWT_SECRET_KEY,
    session_cookie="shortparse_session",
    max_age=JWT_EXPIRATION_HOURS * 3600,
)

# Register authentication routes
app.include_router(oauth_router)


class AnalyzeRequest(BaseModel):
    report_url: str


class JobRequest(BaseModel):
    report_url: str


@app.on_event("startup")
def startup_check() -> None:
    if has_warcraftlogs_credentials():
        logger.info("Warcraft Logs credentials detected")
    else:
        logger.warning("Warcraft Logs credentials are missing")

    from shortparse.cache import HAS_REDIS
    from shortparse.settings import REDIS_PASSWORD, REDIS_HOST, REDIS_PORT

    if HAS_REDIS:
        logger.info("Redis cache backend connected successfully at %s:%s", REDIS_HOST, REDIS_PORT)
    else:
        if REDIS_PASSWORD:
            logger.error(
                "Redis connection failed at %s:%s but credentials were provided! "
                "Falling back to disk cache.",
                REDIS_HOST,
                REDIS_PORT,
            )
        else:
            logger.info("Redis cache backend not running. Falling back to disk cache.")


@app.get("/health")
def health_check() -> dict:
    logger.info("Health check requested")

    return {
        "status": "ok",
    }


@app.get("/version")
def version() -> dict:
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
    }


@app.post("/jobs")
def create_analysis_job(
    request: JobRequest,
    http_request: Request,
    background_tasks: BackgroundTasks,
) -> dict:
    report_code = extract_report_code(request.report_url)

    job = create_job(
        request.report_url,
        report_code,
    )
    
    # Associate the job with the logged-in user if authenticated
    job["user_id"] = http_request.session.get("user_id")

    save_job(job)

    background_tasks.add_task(
        run_analysis_job,
        job,
    )

    logger.info(
        "Created analysis job: job_id=%s report=%s",
        job["job_id"],
        report_code,
    )

    return job


@app.get("/jobs")
def get_jobs() -> dict:
    return {
        "jobs": list_jobs(),
    }


@app.get("/jobs/{job_id}")
def get_analysis_job(job_id: str) -> dict:
    job = get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return job


@app.get("/jobs/{job_id}/summary")
def get_job_summary(job_id: str) -> dict:
    job = get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "report_code": job["report_code"],
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
        "has_result": bool(job.get("result_path")),
        "error": job.get("error"),

        # Live console fields
        "progress": job.get("progress", 0),
        "current_step": job.get("current_step", job["status"]),
        "logs": job.get("logs", []),
    }


@app.post("/jobs/{job_id}/run")
def run_job(job_id: str) -> dict:
    job = get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    updated_job = run_analysis_job(job)

    if not updated_job:
        raise HTTPException(
            status_code=500,
            detail="Job failed to run",
        )

    return updated_job


@app.get("/jobs/{job_id}/result")
def get_job_result(job_id: str) -> dict:
    job = get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    result_path = job.get("result_path")

    if not result_path:
        raise HTTPException(
            status_code=404,
            detail="Job result not available yet",
        )

    path = Path(result_path)

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Job result file not found",
        )

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


@app.post("/analyze")
def analyze_report(request: AnalyzeRequest) -> dict:
    report_code = extract_report_code(request.report_url)

    logger.info(
        "API analysis requested for report %s",
        report_code,
    )

    client = WarcraftLogsClient()
    report = client.get_report_fights(report_code)

    selected = select_best_boss_encounters(report["fights"])

    analyses = []

    for raid_name, fights in selected.items():
        for fight in fights:
            fight_data = client.get_fight_player_data(
                report_code,
                fight["id"],
            )

            events = client.get_fight_events(
                report_code,
                fight["id"],
                fight["startTime"],
                fight["endTime"],
            )

            analysis = build_fight_analysis(
                report_code,
                report["title"],
                fight,
                fight_data,
                events,
            )

            logger.info(
                "Completed fight analysis: report=%s fight_id=%s boss=%s",
                report_code,
                fight["id"],
                analysis["fight"]["name"],
            )

            analysis["raid"] = {
                "name": raid_name,
            }

            analyses.append(
                serialize_analysis(analysis)
            )

    logger.info(
        "Completed report analysis: report=%s fights=%s",
        report_code,
        len(analyses),
    )

    return {
        "report": {
            "code": report_code,
            "title": report["title"],
        },
        "analyses": analyses,
    }