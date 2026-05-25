from datetime import datetime
from sqlalchemy import inspect, text
from shortparse.database import SessionLocal, engine
from shortparse.db_models import Base, Job

# Automatically create all SQLite tables on first store initialization
Base.metadata.create_all(bind=engine)

# Database self-healing: automatically add discord_webhook_url if it is missing
inspector = inspect(engine)
columns = [col['name'] for col in inspector.get_columns('users')]
if 'discord_webhook_url' not in columns:
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN discord_webhook_url VARCHAR"))


def db_job_to_dict(db_job: Job | None) -> dict | None:
    if not db_job:
        return None

    return {
        "job_id": db_job.job_id,
        "user_id": db_job.user_id,
        "status": db_job.status,
        "report_url": db_job.report_url,
        "report_code": db_job.report_code,
        "result_path": db_job.result_path,
        "error": db_job.error,
        "progress": db_job.progress,
        "current_step": db_job.current_step,
        "logs": db_job.logs or [],
        "created_at": db_job.created_at.isoformat() if db_job.created_at else None,
        "updated_at": db_job.updated_at.isoformat() if db_job.updated_at else None,
    }


def save_job(job_dict: dict) -> dict:
    db = SessionLocal()
    try:
        db_job = db.query(Job).filter(Job.job_id == job_dict["job_id"]).first()
        
        created_at = None
        if job_dict.get("created_at"):
            try:
                # ISO format string to datetime
                created_at = datetime.fromisoformat(job_dict["created_at"].replace("Z", "+00:00"))
            except Exception:
                created_at = datetime.utcnow()

        if not db_job:
            db_job = Job(
                job_id=job_dict["job_id"],
                user_id=job_dict.get("user_id"),
                status=job_dict["status"],
                report_url=job_dict["report_url"],
                report_code=job_dict["report_code"],
                result_path=job_dict.get("result_path"),
                error=job_dict.get("error"),
                progress=job_dict.get("progress", 0),
                current_step=job_dict.get("current_step", "Queued"),
                logs=job_dict.get("logs", []),
                created_at=created_at or datetime.utcnow(),
                updated_at=created_at or datetime.utcnow(),
            )
            db.add(db_job)
        else:
            db_job.status = job_dict["status"]
            db_job.result_path = job_dict.get("result_path")
            db_job.error = job_dict.get("error")
            db_job.progress = job_dict.get("progress", db_job.progress)
            db_job.current_step = job_dict.get("current_step", db_job.current_step)
            db_job.logs = job_dict.get("logs", db_job.logs)
            db_job.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_job)
        return db_job_to_dict(db_job)
    finally:
        db.close()


def get_job(job_id: str) -> dict | None:
    db = SessionLocal()
    try:
        db_job = db.query(Job).filter(Job.job_id == job_id).first()
        return db_job_to_dict(db_job)
    finally:
        db.close()


def list_jobs() -> list[dict]:
    db = SessionLocal()
    try:
        db_jobs = db.query(Job).order_by(Job.created_at.desc()).all()
        return [db_job_to_dict(job) for job in db_jobs]
    finally:
        db.close()


def mark_job_running(job_id: str) -> dict | None:
    db = SessionLocal()
    try:
        db_job = db.query(Job).filter(Job.job_id == job_id).first()
        if db_job:
            db_job.status = "running"
            db_job.updated_at = datetime.utcnow()
            db.commit()
            return db_job_to_dict(db_job)
        return None
    finally:
        db.close()


def mark_job_completed(
    job_id: str,
    result_path: str | None = None,
) -> dict | None:
    db = SessionLocal()
    try:
        db_job = db.query(Job).filter(Job.job_id == job_id).first()
        if db_job:
            db_job.status = "completed"
            if result_path is not None:
                db_job.result_path = result_path
            db_job.updated_at = datetime.utcnow()
            db.commit()
            return db_job_to_dict(db_job)
        return None
    finally:
        db.close()


def mark_job_failed(
    job_id: str,
    error: str,
) -> dict | None:
    db = SessionLocal()
    try:
        db_job = db.query(Job).filter(Job.job_id == job_id).first()
        if db_job:
            db_job.status = "failed"
            db_job.error = error
            db_job.updated_at = datetime.utcnow()
            db.commit()
            return db_job_to_dict(db_job)
        return None
    finally:
        db.close()


def append_job_log(
    job_id: str,
    message: str,
    level: str = "info",
    progress: int | None = None,
    current_step: str | None = None,
) -> dict | None:
    db = SessionLocal()
    try:
        db_job = db.query(Job).filter(Job.job_id == job_id).first()
        if db_job:
            # Append new log entry to logs list
            current_logs = list(db_job.logs or [])
            current_logs.append({
                "time": datetime.utcnow().isoformat(),
                "level": level,
                "message": message,
            })
            db_job.logs = current_logs

            if progress is not None:
                db_job.progress = max(0, min(100, progress))

            if current_step is not None:
                db_job.current_step = current_step

            db_job.updated_at = datetime.utcnow()
            db.commit()
            return db_job_to_dict(db_job)
        return None
    finally:
        db.close()