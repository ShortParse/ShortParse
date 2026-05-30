from dotenv import load_dotenv

load_dotenv()

import os
import json
import queue
import threading
import time
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

# Create a thread-safe Priority Queue
JOB_QUEUE = queue.PriorityQueue()

def queue_worker():
    """
    Background worker thread that processes jobs sequentially from the PriorityQueue.
    Always executes higher priority jobs first, falling back to FIFO order.
    """
    logger.info("Starting background job queue worker thread...")
    while True:
        try:
            # Block until a job is available
            priority, timestamp, job = JOB_QUEUE.get()
            logger.info(
                "Worker pulled job %s from queue (Priority: %s)", 
                job["job_id"], 
                "High" if priority == 1 else "Standard"
            )
            
            try:
                # Update status to processing
                job_data = get_job(job["job_id"])
                if job_data:
                    run_analysis_job(job_data)
                    
                    # Auto-post to Discord if enabled and premium
                    completed_job = get_job(job["job_id"])
                    if completed_job and completed_job.get("status") == "completed" and completed_job.get("user_id"):
                        from shortparse.database import SessionLocal
                        from shortparse.db_models import User
                        
                        with SessionLocal() as db:
                            user = db.query(User).filter(User.id == completed_job["user_id"]).first()
                            if user and user.is_premium and user.discord_webhook_url and user.discord_auto_post:
                                logger.info("Auto-posting completed job %s to Discord for user %s", job["job_id"], user.username)
                                dispatch_discord_summary_embed_helper(
                                    webhook_url=user.discord_webhook_url,
                                    job_id=completed_job["job_id"],
                                    result_path=completed_job["result_path"],
                                    origin=os.getenv("FRONTEND_URL", "https://dev.shortparse.com")
                                )
            except Exception as e:
                logger.error("Error processing queued job %s: %s", job.get("job_id"), e)
            finally:
                JOB_QUEUE.task_done()
        except Exception as e:
            logger.error("Queue worker encountered an error: %s", e)
            time.sleep(1)

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

# Register Guild Suite routes
from shortparse.server.guild import router as guild_router
app.include_router(guild_router)


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

    # Dynamic SQLite migration to ensure users table has gemini_api_key and excluded_ledger_players columns
    from shortparse.database import engine
    from sqlalchemy import text
    try:
        with engine.begin() as conn:
            result = conn.execute(text("PRAGMA table_info(users)")).fetchall()
            columns = [row[1] for row in result]
            if "gemini_api_key" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN gemini_api_key VARCHAR"))
                logger.info("Migrated users table to include gemini_api_key column.")
            if "excluded_ledger_players" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN excluded_ledger_players TEXT"))
                logger.info("Migrated users table to include excluded_ledger_players column.")
    except Exception as e:
        logger.warning("Auto-migration of users table failed: %s", e)

    # Patreon integration credentials validation
    from shortparse.settings import PATREON_CLIENT_ID, PATREON_CLIENT_SECRET, PATREON_REDIRECT_URI
    import requests

    if not PATREON_CLIENT_ID or not PATREON_CLIENT_SECRET:
        logger.warning("Patreon integration credentials are missing or incomplete in settings")
    else:
        try:
            response = requests.post(
                "https://www.patreon.com/api/oauth2/token",
                data={
                    "grant_type": "authorization_code",
                    "code": "startup_validate_test_code_dummy",
                    "redirect_uri": PATREON_REDIRECT_URI,
                    "client_id": PATREON_CLIENT_ID,
                    "client_secret": PATREON_CLIENT_SECRET,
                },
                timeout=8,
            )
            # If Client credentials are bad, Patreon returns invalid_client (usually HTTP 401)
            # If they are good, Patreon accepts the client but rejects the dummy code (usually HTTP 400 invalid_grant)
            payload = response.json()
            if payload.get("error") == "invalid_client":
                logger.error("Patreon integration credentials validation FAILED: Invalid Client ID or Client Secret")
            else:
                logger.info("Patreon integration credentials validated successfully")
        except Exception as e:
            logger.warning("Unable to reach Patreon API to validate credentials: %s", e)

    # Gemini AI Coach API Key validation
    from shortparse.settings import GEMINI_API_KEY
    if not GEMINI_API_KEY:
        logger.warning("Gemini API Key is missing in settings (GEMINI_API_KEY). Using Mock Coach fallback engine.")
    else:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            response = requests.post(
                url,
                json={
                    "contents": [{"parts": [{"text": "Say ok"}]}]
                },
                headers={"Content-Type": "application/json"},
                timeout=8,
            )
            if response.status_code == 200:
                logger.info("Gemini API key validated and communication successful")
            else:
                logger.error(
                    "Gemini API key validation FAILED (status %s): %s",
                    response.status_code,
                    response.text
                )
        except Exception as e:
            logger.warning("Unable to reach Gemini API to validate credentials: %s", e)

    # Start the background priority queue worker thread as a daemon
    worker_thread = threading.Thread(target=queue_worker, daemon=True)
    worker_thread.start()


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
) -> dict:
    report_code = extract_report_code(request.report_url)

    job = create_job(
        request.report_url,
        report_code,
    )
    
    # Associate the job with the logged-in user if authenticated
    job["user_id"] = http_request.session.get("user_id")

    save_job(job)

    # Determine Priority (1 = High/Premium, 2 = Standard)
    priority = 2
    
    from shortparse.settings import PATREON_PRIORITY_QUEUE_ENABLED
    if PATREON_PRIORITY_QUEUE_ENABLED and job["user_id"]:
        from shortparse.database import SessionLocal
        from shortparse.db_models import User
        
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == job["user_id"]).first()
            if user:
                from shortparse.settings import BYPASS_PREMIUM_USERNAMES
                is_bypass = user.username.strip().lower() in BYPASS_PREMIUM_USERNAMES if user.username else False
                if user.is_premium or is_bypass:
                    priority = 1

    # Enqueue to our Priority Queue
    JOB_QUEUE.put((priority, time.time(), job))

    logger.info(
        "Enqueued analysis job: job_id=%s report=%s (Priority: %s)",
        job["job_id"],
        report_code,
        "High" if priority == 1 else "Standard"
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

    # Real-Time Autopilot: Self-heal empty synced logs when boss content starts
    if job.get("status") == "completed" and job.get("result_path"):
        result_path = Path(job["result_path"])
        if result_path.exists():
            try:
                with open(result_path, "r", encoding="utf-8") as file:
                    result_data = json.load(file)
                
                # If there are no boss analyses, check if fights have been logged on Warcraft Logs
                if not result_data.get("analyses"):
                    report_code = job.get("report_code")
                    if report_code:
                        client = WarcraftLogsClient()
                        report = client.get_report_fights(report_code)
                        from shortparse.selector import select_best_boss_encounters
                        selected = select_best_boss_encounters(report.get("fights", []))
                        
                        if selected:
                            logger.info("Autopilot: New fights detected for empty report %s. Resetting job %s.", report_code, job_id)
                            
                            # Delete the empty result file
                            try:
                                result_path.unlink()
                            except Exception:
                                pass
                                
                            # Reset job in database to queued state
                            from shortparse.jobs.models import utc_now_iso
                            now = utc_now_iso()
                            job["status"] = "queued"
                            job["result_path"] = None
                            job["progress"] = 0
                            job["current_step"] = "Queued"
                            job["logs"] = [{
                                "time": now,
                                "level": "info",
                                "message": "New fights detected! Re-starting analysis job..."
                            }]
                            job = save_job(job)
                            
                            # Re-enqueue the job
                            JOB_QUEUE.put((2, time.time(), job))
            except Exception as e:
                logger.error("Autopilot fight checking failed for job %s: %s", job_id, e)

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


from fastapi import Depends
from sqlalchemy.orm import Session
from shortparse.database import get_db
from shortparse.db_models import User
import requests
from datetime import datetime

def dispatch_discord_summary_embed_helper(
    webhook_url: str,
    job_id: str,
    result_path: str,
    origin: str = "https://shortparse.com",
    analysis_index: int = 0,
) -> bool:
    try:
        path = Path(result_path)
        if not path.exists():
            logger.error("Job result file not found at %s", result_path)
            return False

        with open(path, "r", encoding="utf-8") as file:
            analysis_data = json.load(file)

        analyses = analysis_data.get("analyses", [])
        if not analyses:
            logger.error("No analyses found in the report result at %s", result_path)
            return False

        idx = max(0, min(analysis_index, len(analyses) - 1))
        analysis = analyses[idx]

        fight = analysis.get("fight", {})
        report_title = analysis_data.get("report", {}).get("title", "Raid Report")
        scorecard = analysis.get("scorecard", [])
        issues = analysis.get("issues", [])

        difficulty_map = {
            1: "LFR", 2: "Normal", 3: "Normal", 4: "Heroic", 5: "Mythic",
            10: "Normal", 14: "Normal", 15: "Heroic", 16: "Mythic", 17: "LFR"
        }
        difficulty = difficulty_map.get(fight.get("difficulty"), "Normal")
        result_label = "Kill" if fight.get("kill") else f"Wipe ({fight.get('boss_percentage') or '?'}% HP)"

        # Formatted Duration
        duration_sec = fight.get("duration_seconds") or 0
        duration_min = int(duration_sec // 60)
        duration_rem = int(duration_sec % 60)
        duration_str = f"{duration_min}:{duration_rem:02d}"

        # Calculate average grade
        grade_points = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
        reverse_points = {5: "S", 4: "A", 3: "B", 2: "C", 1: "D", 0: "F"}
        
        grades = [grade_points.get(row.get("grade"), 0) for row in scorecard if "grade" in row]
        avg_grade = "—"
        if grades:
            avg_points = sum(grades) / len(grades)
            avg_grade = reverse_points.get(round(avg_points), "C")

        # Extract Top Performers
        sorted_performers = sorted(scorecard, key=lambda x: grade_points.get(x.get("grade"), 0), reverse=True)
        top_performers = sorted_performers[:3]
        top_perf_str = ""
        for row in top_performers:
            top_perf_str += f"• **{row.get('player')}** — Grade **{row.get('grade')}**\n"
        if not top_perf_str:
            top_perf_str = "None recorded."

        # Extract Area of Concern
        worst_player_row = scorecard[0] if scorecard else None
        worst_player_name = worst_player_row.get("player", "None") if worst_player_row else "None"
        worst_player_grade = worst_player_row.get("grade", "-") if worst_player_row else "-"
        worst_player_issue = worst_player_row.get("top_issue", "Rotational gaps detected") if worst_player_row else "—"

        # Color code: green for Kill, red/orange for Wipe
        embed_color = 3718392
        if fight.get("kill"):
            embed_color = 4906624
        else:
            embed_color = 16478597

        report_link = f"{origin.rstrip('/')}/report/{job_id}/{idx}/scorecard"

        discord_payload = {
            "username": "ShortParse",
            "avatar_url": "https://raw.githubusercontent.com/ShortParse/ShortParse-Web/main/images/apple-touch-icon.png",
            "embeds": [
                {
                    "title": f"🛡️ ShortParse Raid Summary: {fight.get('name', 'Boss')} ({difficulty})",
                    "description": f"**Report:** *{report_title}*\n**Result:** **{result_label}** • **{duration_str}** Duration",
                    "color": embed_color,
                    "fields": [
                        {
                            "name": "📊 Roster Stats",
                            "value": f"**Players:** {len(scorecard)}\n**Raid Average Grade:** {avg_grade}\n**Total Issues Logged:** {len(issues)}",
                            "inline": True
                        },
                        {
                            "name": "🏆 Top Performers",
                            "value": top_perf_str,
                            "inline": True
                        },
                        {
                            "name": "⚠️ Areas of Concern",
                            "value": f"**Top Concern:** {worst_player_name} ({worst_player_grade})\n**Primary Fault:** {worst_player_issue}",
                            "inline": False
                        }
                    ],
                    "footer": {
                        "text": "ShortParse - Automated Warcraft Logs Reviews"
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                    "url": report_link
                }
            ]
        }

        response = requests.post(webhook_url, json=discord_payload, timeout=15)
        if response.status_code not in (200, 204):
            logger.error("Discord API returned status %s: %s", response.status_code, response.text)
            return False

        return True
    except Exception as e:
        logger.error("Failed to automatically post to Discord: %s", e)
        return False


class DiscordPostRequest(BaseModel):
    analysis_index: int = 0


@app.post("/jobs/{job_id}/discord")
def post_job_to_discord(
    job_id: str,
    request: Request,
    payload: DiscordPostRequest,
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    from shortparse.settings import BYPASS_PREMIUM_USERNAMES
    is_bypass = user.username.strip().lower() in BYPASS_PREMIUM_USERNAMES if user.username else False

    if not user.is_premium and not is_bypass:
        raise HTTPException(
            status_code=403,
            detail="Discord Webhook integration is a Premium feature. Support us on Patreon to unlock!",
        )

    if not user.discord_webhook_url:
        raise HTTPException(
            status_code=400,
            detail="You must configure a Discord Webhook URL in your Settings first.",
        )

    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    result_path = job.get("result_path")
    if not result_path:
        raise HTTPException(status_code=400, detail="Job results are not available yet.")

    origin = request.headers.get("origin") or "https://shortparse.com"
    success = dispatch_discord_summary_embed_helper(
        webhook_url=user.discord_webhook_url,
        job_id=job_id,
        result_path=result_path,
        origin=origin,
        analysis_index=payload.analysis_index,
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Failed to post summary to Discord.",
        )

    return {"status": "success", "message": "Raid summary posted to Discord!"}


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


import sys
import importlib
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

@app.get("/encounters")
@app.get("/api/encounters")
def get_encounters():
    base_dir = Path(__file__).resolve().parent.parent / "data" / "encounters"
    
    # Discover raid directories dynamically
    raids_dirs = []
    if base_dir.exists():
        for item in sorted(base_dir.iterdir()):
            if item.is_dir() and not item.name.startswith("__") and not item.name.startswith("."):
                raids_dirs.append(item.name)
    
    result = []
    
    for raid_id in raids_dirs:
        raid_path = base_dir / raid_id
        if not raid_path.is_dir():
            continue
            
        # Clean title casing and specific custom name formatting
        raid_name = raid_id.replace("_", " ").title()
        if raid_id == "the_voidspire":
            raid_name = "The Voidspire"
        elif raid_id == "the_dreamrift":
            raid_name = "The Dreamrift"
        elif raid_id == "march_on_queldanas":
            raid_name = "March on Quel'Danas"
            
        bosses = []
        
        for filename in sorted(raid_path.iterdir()):
            if not filename.name.endswith(".py") or filename.name == "__init__.py":
                continue
                
            module_name = filename.name[:-3]
            full_module_path = f"shortparse.data.encounters.{raid_id}.{module_name}"
            
            try:
                if full_module_path in sys.modules:
                    module = importlib.reload(sys.modules[full_module_path])
                else:
                    module = importlib.import_module(full_module_path)
                    
                encounter_name = getattr(module, "ENCOUNTER_NAME", module_name.replace("_", " ").title())
                encounter_id = getattr(module, "ENCOUNTER_ID", None)
                avoidable_damage = getattr(module, "AVOIDABLE_DAMAGE", {})
                
                # Find all mechanics defined in the module
                mechanics = []
                for key, val in module.__dict__.items():
                    if key.isupper() and isinstance(val, dict) and "name" in val and "severity" in val:
                        spell_ids = []
                        for spell_id, mech in avoidable_damage.items():
                            if mech is val or mech.get("name") == val.get("name"):
                                if spell_id not in spell_ids:
                                    spell_ids.append(spell_id)
                        
                        if not spell_ids and "spell_ids" in val:
                            spell_ids = val["spell_ids"]
                            
                        applies_to_val = val.get("applies_to", [])
                        
                        mechanic_data = {
                            "variable_name": key,
                            "name": val.get("name", ""),
                            "severity": val.get("severity", "Warning"),
                            "avoidable": val.get("avoidable", True),
                            "category": val.get("category", "avoidable_damage"),
                            "failure_type": val.get("failure_type", "avoidable_damage"),
                            "counts_as_failure": val.get("counts_as_failure", True),
                            "max_reasonable_hits": val.get("max_reasonable_hits", 1),
                            "score_per_hit": val.get("score_per_hit", 0),
                            "applies_to": applies_to_val,
                            "spell_ids": spell_ids,
                            "note": val.get("note", ""),
                            "recommendation": val.get("recommendation", ""),
                            "wcl_type": val.get("wcl_type", "damage_taken"),
                            "minimum_soakers": val.get("minimum_soakers")
                        }
                        mechanics.append(mechanic_data)
                
                mechanics.sort(key=lambda m: m["name"])
                
                bosses.append({
                    "id": encounter_id,
                    "filename": filename.name,
                    "name": encounter_name,
                    "mechanics": mechanics
                })
            except Exception as e:
                logger.error(f"Error loading boss module {full_module_path}: {e}")
                
        result.append({
            "id": raid_id,
            "name": raid_name,
            "bosses": bosses
        })
        
    return result

@app.get("/builder", response_class=HTMLResponse)
def serve_builder(request: Request):
    possible_paths = [
        Path(__file__).resolve().parent.parent.parent.parent / "ShortParse-Web" / "index.html",
        Path(__file__).resolve().parent.parent / "ShortParse-Web" / "index.html",
        Path("/storage/ShortParse-Web/index.html"),
        Path("/app/index.html"),
    ]
    
    for path in possible_paths:
        if path.exists():
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
            return HTMLResponse(content=content)
            
    raise HTTPException(status_code=404, detail="index.html not found")


@app.get("/admin", response_class=HTMLResponse)
def serve_admin(request: Request):
    possible_paths = [
        Path(__file__).resolve().parent.parent.parent.parent / "ShortParse-Web" / "index.html",
        Path(__file__).resolve().parent.parent / "ShortParse-Web" / "index.html",
        Path("/storage/ShortParse-Web/index.html"),
        Path("/app/index.html"),
    ]
    
    for path in possible_paths:
        if path.exists():
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
            return HTMLResponse(content=content)
            
    raise HTTPException(status_code=404, detail="index.html not found")


@app.get("/admin/stats")
def get_admin_stats(request: Request, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated.")
        
    from shortparse.settings import ADMIN_USERNAMES
    normalized_username = username.strip().lower()
    if normalized_username not in ADMIN_USERNAMES:
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required.")

    from shortparse.db_models import Job, User, LinkedAccount
    from sqlalchemy import func

    # 1. User stats
    total_users = db.query(User).count()
    total_reports = db.query(Job).count()
    
    # Most active user (excluding anyone in ADMIN_USERNAMES)
    most_active = (
        db.query(User.username, func.count(Job.job_id).label("job_count"))
        .join(Job, User.id == Job.user_id)
        .group_by(User.id)
        .all()
    )
    # Filter out admin usernames (case-insensitive)
    most_active_filtered = [
        item for item in most_active
        if item[0] and item[0].strip().lower() not in ADMIN_USERNAMES
    ]
    if most_active_filtered:
        most_active_filtered.sort(key=lambda x: x[1], reverse=True)
        most_active_user = most_active_filtered[0][0]
        most_active_user_jobs = most_active_filtered[0][1]
    else:
        most_active_user = "None"
        most_active_user_jobs = 0

    # Patreon members count (premium users that are not bypass admins)
    premium_users = db.query(User).filter(User.is_premium == True).all()
    patreon_members = sum(
        1 for u in premium_users
        if u.username and u.username.strip().lower() not in ADMIN_USERNAMES
    )
    
    # Patreon adoption ratio
    patreon_adoption_ratio = 0.0
    if total_users > 0:
        patreon_adoption_ratio = round((patreon_members / total_users) * 100, 2)

    # 2. Cooldown stats
    import shortparse.data.cooldowns as cd
    from shortparse.data.cooldowns import RAID_COOLDOWNS
    cd_dir = Path(cd.__file__).resolve().parent
    classes = [d for d in cd_dir.iterdir() if d.is_dir() and not d.name.startswith("__")]
    total_classes = len(classes)
    
    total_specs = 0
    for d in classes:
        for f in d.iterdir():
            if f.suffix == ".py" and not f.name.startswith("__") and f.name != "shared.py":
                total_specs += 1
                
    total_spells = len(RAID_COOLDOWNS)

    # 3. Encounter stats
    from shortparse.data.encounters.registry import ENCOUNTER_MODULES
    total_raid_zones = len(ENCOUNTER_MODULES)
    
    total_bosses = 0
    total_mechanics = 0
    raid_zones_info = []
    
    for module in ENCOUNTER_MODULES:
        boss_map = getattr(module, "AVOIDABLE_DAMAGE_BY_ENCOUNTER_ID", {})
        boss_count = len(boss_map)
        total_bosses += boss_count
        
        mechanics_in_raid = set()
        for encounter_id, avoidable_damage in boss_map.items():
            for spell_id, mechanic in avoidable_damage.items():
                if isinstance(mechanic, dict) and "name" in mechanic:
                    mechanics_in_raid.add(mechanic["name"])
        total_mechanics += len(mechanics_in_raid)
        
        mod_name = module.__name__.split(".")[-1]
        display_name = mod_name.replace("_", " ").title()
        if mod_name == "march_on_queldanas":
            display_name = "March on Quel'Danas"
        elif mod_name == "the_dreamrift":
            display_name = "The Dreamrift"
        elif mod_name == "the_voidspire":
            display_name = "The Voidspire"
            
        raid_zones_info.append({
            "name": display_name,
            "bosses": boss_count,
            "mechanics": len(mechanics_in_raid)
        })

    # 4. Queue / System Activity Stats
    queued_jobs = db.query(Job).filter(Job.status == "queued").count()
    running_jobs = db.query(Job).filter(Job.status == "running").count()
    completed_jobs = db.query(Job).filter(Job.status == "completed").count()
    failed_jobs = db.query(Job).filter(Job.status == "failed").count()
    
    recent_jobs_query = db.query(Job).order_by(Job.created_at.desc()).limit(5).all()
    recent_jobs = []
    for job in recent_jobs_query:
        username_label = "Anonymous"
        if job.user_id:
            u = db.query(User).filter(User.id == job.user_id).first()
            if u:
                username_label = u.username
        recent_jobs.append({
            "job_id": job.job_id,
            "report_code": job.report_code,
            "status": job.status,
            "username": username_label,
            "created_at": job.created_at.isoformat() if job.created_at else None
        })

    # 5. System Health Info
    from shortparse.cache import HAS_REDIS
    from shortparse.settings import REDIS_HOST, REDIS_PORT
    from shortparse.database import DB_PATH
    
    db_size_bytes = 0
    try:
        if DB_PATH.exists():
            db_size_bytes = DB_PATH.stat().st_size
    except Exception:
        pass
        
    db_size_mb = round(db_size_bytes / (1024 * 1024), 2)
    
    redis_status = "Connected" if HAS_REDIS else "Disconnected (Disk Cache Fallback)"
    redis_info = f"{REDIS_HOST}:{REDIS_PORT}" if HAS_REDIS else "None"

    return {
        "user_stats": {
            "total_users": total_users,
            "total_reports": total_reports,
            "most_active_user": most_active_user,
            "most_active_user_jobs": most_active_user_jobs,
            "patreon_members": patreon_members,
            "patreon_adoption_ratio": patreon_adoption_ratio
        },
        "cooldown_stats": {
            "total_classes": total_classes,
            "total_specs": total_specs,
            "total_spells": total_spells
        },
        "encounter_stats": {
            "total_raid_zones": total_raid_zones,
            "total_bosses": total_bosses,
            "total_mechanics": total_mechanics,
            "raid_zones": raid_zones_info
        },
        "queue_stats": {
            "queued": queued_jobs,
            "running": running_jobs,
            "completed": completed_jobs,
            "failed": failed_jobs,
            "recent_jobs": recent_jobs
        },
        "system_health": {
            "redis_status": redis_status,
            "redis_info": redis_info,
            "db_size_mb": db_size_mb
        }
    }


class GitPullRequest(BaseModel):
    repo: str  # "web" or "backend"


@app.post("/admin/actions/git-pull")
def admin_git_pull(request: Request, payload: GitPullRequest, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated.")
        
    from shortparse.settings import ADMIN_USERNAMES
    if username.strip().lower() not in ADMIN_USERNAMES:
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required.")
        
    import subprocess
    from pathlib import Path
    
    # Determine repository path
    base_dir = Path(__file__).resolve().parent.parent.parent
    if payload.repo == "backend":
        repo_path = base_dir
    elif payload.repo == "web":
        repo_path = Path("/var/www/html")
        if not repo_path.exists() or not (repo_path / ".git").exists():
            return {
                "status": "skipped",
                "message": "Website repository not found or not initialized as a git repository on this VM. This is expected in a multi-VM environment (like Dev) where the frontend is hosted on a separate virtual machine. This action is fully operational on single-system environments (like the Live server)."
            }
    else:
        raise HTTPException(status_code=400, detail="Invalid repository identifier.")
        
    try:
        # 1. Determine local branch
        branch_res = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=10,
            check=True
        )
        branch = branch_res.stdout.strip() or "dev"
        
        # 2. Run git pull origin <branch>
        pull_res = subprocess.run(
            ["git", "pull", "origin", branch],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=20,
            check=True
        )
        
        return {
            "status": "success",
            "branch": branch,
            "output": pull_res.stdout.strip()
        }
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() or e.stdout.strip() or str(e)
        logger.error(f"Git pull failed in {repo_path}: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Git pull failed: {error_msg}")
    except Exception as e:
        logger.error(f"Unexpected error during git pull in {repo_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/actions/restart-api")
def admin_restart_api(request: Request, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated.")
        
    from shortparse.settings import ADMIN_USERNAMES
    if username.strip().lower() not in ADMIN_USERNAMES:
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required.")
        
    import subprocess
    import threading
    import time
    
    def trigger_restart():
        time.sleep(1)
        try:
            logger.info("Executing systemctl restart shortparse.service...")
            subprocess.run(["sudo", "systemctl", "restart", "shortparse.service"], check=True)
        except Exception as e:
            logger.error(f"Failed to restart service: {e}")
            
    threading.Thread(target=trigger_restart, daemon=True).start()
    
    return {
        "status": "success",
        "message": "API restart command dispatched successfully. Server will be online shortly."
    }


class UpdateEncountersRequest(BaseModel):
    zone_id: int


def ask_gemini_generator(prompt_text: str) -> str:
    from shortparse.settings import GEMINI_API_KEY
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured in settings.")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt_text}]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 8192
        }
    }
    response = requests.post(url, json=payload, headers=headers, timeout=40)
    response.raise_for_status()
    result = response.json()
    candidates = result.get("candidates", [])
    if candidates:
        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return text.strip()
    raise RuntimeError(f"Gemini API returned empty response: {response.text}")


@app.post("/admin/actions/update-encounters")
def admin_update_encounters(
    request: Request,
    payload: UpdateEncountersRequest,
    db: Session = Depends(get_db)
):
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated.")
        
    from shortparse.settings import ADMIN_USERNAMES
    if username.strip().lower() not in ADMIN_USERNAMES:
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required.")
        
    zone_id = payload.zone_id
    
    # 1. Fetch Zone and Boss list from WCL
    wcl_client = WarcraftLogsClient()
    zone_query = """
    query($zoneID: Int!) {
      worldData {
        zone(id: $zoneID) {
          name
          encounters {
            id
            name
          }
        }
      }
    }
    """
    try:
        zone_data = wcl_client.graphql(zone_query, {"zoneID": zone_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query WCL Zone: {e}")
        
    zone_info = zone_data.get("worldData", {}).get("zone")
    if not zone_info:
        raise HTTPException(status_code=404, detail=f"Zone ID {zone_id} not found in WCL database.")
        
    raid_name = zone_info.get("name")
    encounters = zone_info.get("encounters", []) or []
    
    if not encounters:
        raise HTTPException(status_code=404, detail=f"Raid zone \"{raid_name}\" contains no active boss encounters.")
        
    import re
    def slugify(text: str) -> str:
        slug = text.strip().lower().replace(" ", "_")
        return re.sub(r"[^a-z0-9_]", "", slug)
        
    raid_slug = slugify(raid_name)
    
    # Create raid directory
    raid_dir = Path(__file__).resolve().parent.parent / "data" / "encounters" / raid_slug
    raid_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize Blizzard client
    from shortparse.server.bnet_client import BlizzardClient
    bnet_client = BlizzardClient()
    
    processed_bosses = []
    skipped_bosses = []
    
    # 2. Process each boss
    for boss in encounters:
        boss_id = boss["id"]
        boss_name = boss["name"]
        boss_slug = slugify(boss_name)
        
        # Scrape 2 unique rankings to get elite reports
        rankings_query = """
        query($encounterID: Int!, $className: String!, $specName: String!) {
          worldData {
            encounter(id: $encounterID) {
              characterRankings(
                difficulty: 5,
                className: $className,
                specName: $specName
              )
            }
          }
        }
        """
        report_fights = []
        spec_queries = [
            ("Priest", "Holy"),
            ("Paladin", "Holy"),
            ("Warrior", "Protection")
        ]
        for className, specName in spec_queries:
            try:
                res = wcl_client.graphql(rankings_query, {
                    "encounterID": boss_id,
                    "className": className,
                    "specName": specName
                })
                payload = res.get("worldData", {}).get("encounter", {}).get("characterRankings", {}) or {}
                rankings = payload.get("rankings", []) or []
                for r in rankings:
                    report = r.get("report") or {}
                    code = report.get("code")
                    fight_id = report.get("fightID")
                    if code and fight_id and (code, fight_id) not in report_fights:
                        report_fights.append((code, fight_id))
                        if len(report_fights) >= 2:
                            break
                if len(report_fights) >= 2:
                    break
            except Exception:
                continue
                
        if not report_fights:
            skipped_bosses.append(f"{boss_name} (No reports found on WCL)")
            continue
            
        # Compile DamageTaken events across reports
        spell_damage = {}
        damage_query = """
        query($reportCode: String!, $fightIDs: [Int]) {
          reportData {
            report(code: $reportCode) {
              masterData {
                abilities {
                  gameID
                  name
                }
              }
              events(
                fightIDs: $fightIDs
                dataType: DamageTaken
                limit: 1000
              ) {
                data
              }
            }
          }
        }
        """
        for code, fight_id in report_fights:
            try:
                events_res = wcl_client.graphql(damage_query, {
                    "reportCode": code,
                    "fightIDs": [fight_id]
                })
                report_payload = events_res.get("reportData", {}).get("report") or {}
                events = report_payload.get("events", {}).get("data", []) or []
                abilities = report_payload.get("masterData", {}).get("abilities", []) or []
                ability_map = {a["gameID"]: a["name"] for a in abilities if a.get("gameID") is not None}
                
                for ev in events:
                    spell_id = ev.get("abilityGameID")
                    if not spell_id:
                        continue
                    amount = int(ev.get("amount") or 0)
                    target_id = ev.get("targetID")
                    
                    if spell_id not in spell_damage:
                        spell_name = ability_map.get(spell_id, f"Spell {spell_id}")
                        spell_damage[spell_id] = {
                            "id": spell_id,
                            "name": spell_name,
                            "hits": 0,
                            "damage": 0,
                            "targets": set()
                        }
                    
                    spell_damage[spell_id]["hits"] += 1
                    spell_damage[spell_id]["damage"] += amount
                    if target_id:
                        spell_damage[spell_id]["targets"].add(target_id)
            except Exception:
                continue
                
        if not spell_damage:
            skipped_bosses.append(f"{boss_name} (No damage taken events recorded)")
            continue
            
        # Select top 12 damage spells sorted by hits * total damage
        sorted_spells = sorted(
            spell_damage.values(),
            key=lambda x: -(x["hits"] * x["damage"]),
        )
        
        telemetry_lines = []
        for sp in sorted_spells[:12]:
            spell_id = sp["id"]
            name = sp["name"]
            hits = sp["hits"]
            dmg = sp["damage"]
            targets_count = len(sp["targets"])
            
            # Enrich from Blizzard API
            bnet_info = bnet_client.get_spell_info(spell_id)
            if bnet_info:
                bnet_desc = bnet_info.get("description", "")
                telemetry_lines.append(
                    f"* Spell ID {spell_id} (Official Name: \"{bnet_info['name']}\")\n"
                    f"  - Hits: {hits} | Total Damage: {dmg:,} | Players Hit: {targets_count}\n"
                    f"  - Tooltip: \"{bnet_desc}\""
                )
            else:
                telemetry_lines.append(
                    f"* Spell ID {spell_id} (Name in log: \"{name}\")\n"
                    f"  - Hits: {hits} | Total Damage: {dmg:,} | Players Hit: {targets_count}\n"
                    f"  - Tooltip: NOT FOUND in Blizzard official database (Custom Boss Mechanic)"
                )
                
        telemetry_text = "\n".join(telemetry_lines)
        
        # 3. Query Gemini to write the Python Module
        prompt_text = f"""
You are an expert World of Warcraft raid analysis developer.
Your task is to write a highly accurate World of Warcraft encounter mechanic module in Python.
The module must conform precisely to the following `Mechanic` schema:

class Mechanic(TypedDict, total=False):
    name: str  # The name of the mechanic (e.g. "Avenger's Shield")
    severity: Literal["Info", "Minor", "Major", "Critical"]
    avoidable: bool  # True if players can dodge/mitigate, False otherwise
    category: str  # Must be one of the MechanicCategory literals listed below
    failure_type: str  # Must be one of the MechanicFailureType literals listed below
    counts_as_failure: bool  # True if it counts as a failed mechanic count
    max_reasonable_hits: int  # Max hits allowed per fight (usually 0 or 1, or 2 for tank buster swaps)
    score_per_hit: int  # Penalty score per hit (0 to 100)
    applies_to: list[str]  # e.g., ALL_ROLES, NON_TANK_ROLES, DPS_ONLY, HEALER_ONLY, TANK_ONLY
    spell_ids: list[int]  # List of WCL spell IDs matching this mechanic
    note: str  # Clinical description of what the mechanic does
    recommendation: str  # Actionable advice on how to avoid it
    wcl_type: str  # Always "damage_taken"

MechanicCategory Literals:
"ground_effect", "swirl", "traveling_projectile", "beam", "frontal", "rear_cone",
"forced_movement", "interrupt", "minimum_soak", "soak_participation", "bad_soak",
"dispel", "spread", "stack", "boss_threat", "boss_range", "tank_buster",
"tank_positioning", "add_management", "add_priority", "corpse_explosion",
"bait", "lane_movement", "debuff_damage"

MechanicFailureType Literals:
"avoidable_damage", "missed_interrupt", "minimum_soak", "zero_participation",
"bad_soak", "missed_dispel", "bad_dispel", "spread_failure", "stack_failure",
"boss_range"

WoW Roles available:
ALL_ROLES = ["tank", "healer", "dps"]
NON_TANK_ROLES = ["healer", "dps"]
DPS_ONLY = ["dps"]
HEALER_ONLY = ["healer"]
TANK_ONLY = ["tank"]

Here is the combat log telemetry and Blizzard Spell API details collected for boss encounter "{boss_name}" (ID: {boss_id}) in the zone "{raid_name}":

--- Telemetry Data ---
{telemetry_text}

INSTRUCTIONS:
1. Examine the spell list. Exclude any standard player utility spells, standard healing spells, potions, enchants, basic attacks (like Melee).
2. For each genuine boss mechanic, draft a `Mechanic` dict constant.
3. Classify its category and failure_type carefully based on its name and description (e.g. if the description mentions consecration or standing in fire, use "ground_effect" and "avoidable_damage").
4. If it's a tank-only mechanic (e.g. tank strike, physical buster), use TANK_ONLY, avoidable=False, counts_as_failure=False, and failure_type="avoidable_damage".
5. At the bottom of the file, define:
   ENCOUNTER_ID = {boss_id}
   ENCOUNTER_NAME = "{boss_name}"
   And define the AVOIDABLE_DAMAGE mapping:
   AVOIDABLE_DAMAGE = {{
       **mechanic_aliases([spell_id], CONSTANT_NAME),
       ...
   }}
6. The Python code must be 100% syntactically valid and import:
   from shortparse.data.encounters.types import Mechanic
   from shortparse.data.encounters.constants import (
       ALL_ROLES, NON_TANK_ROLES, DPS_ONLY, HEALER_ONLY, TANK_ONLY
   )
   from shortparse.data.encounters.mechanic_helper import mechanic_aliases

Output ONLY the raw Python code within ```python and ``` block. Do not include any other markdown chat or greetings.
"""
        try:
            gemini_output = ask_gemini_generator(prompt_text)
            code_match = re.search(r"```python(.*?)```", gemini_output, re.DOTALL)
            if code_match:
                code_content = code_match.group(1).strip()
            else:
                code_content = gemini_output.strip()
                
            boss_file = raid_dir / f"{boss_slug}.py"
            with open(boss_file, "w", encoding="utf-8") as bf:
                bf.write(code_content)
                
            processed_bosses.append((boss_id, boss_name, boss_slug))
        except Exception as gemini_err:
            skipped_bosses.append(f"{boss_name} (Gemini compilation failed: {gemini_err})")
            continue
            
    if not processed_bosses:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate any boss modules. Reasons: {', '.join(skipped_bosses)}"
        )
        
    init_lines = []
    damage_map_entries = []
    for boss_id, boss_name, boss_slug in processed_bosses:
        const_name = boss_slug.upper()
        init_lines.append(f"from .{boss_slug} import AVOIDABLE_DAMAGE as {const_name}")
        damage_map_entries.append(f"    {boss_id}: {const_name},")
        
    init_lines.append("")
    init_lines.append("AVUIDABLE_DAMAGE_BY_ENCOUNTER_ID = {")
    init_lines.extend(damage_map_entries)
    init_lines.append("}")
    # Fixed typo AVUIDABLE -> AVOIDABLE
    init_lines[-2] = "AVOIDABLE_DAMAGE_BY_ENCOUNTER_ID = {"
    
    init_file = raid_dir / "__init__.py"
    with open(init_file, "w", encoding="utf-8") as inf:
        inf.write("\n".join(init_lines))
        
    from shortparse.data.encounters.registry import load_encounter_modules
    load_encounter_modules()
    
    summary_message = f"Successfully generated encounter config for \"{raid_name}\" under data/encounters/{raid_slug}/.\n\n"
    summary_message += f"Generated Bosses:\n" + "\n".join(f"- {name} (ID: {bid})" for bid, name, _ in processed_bosses)
    if skipped_bosses:
        summary_message += f"\n\nSkipped Bosses:\n" + "\n".join(f"- {s}" for s in skipped_bosses)
        
    return {
        "status": "success",
        "raid_name": raid_name,
        "bosses": [name for _, name, _ in processed_bosses],
        "message": summary_message
    }


@app.post("/admin/actions/update-cooldowns")
def admin_update_cooldowns(
    request: Request,
    db: Session = Depends(get_db)
):
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated.")
        
    from shortparse.settings import ADMIN_USERNAMES
    if username.strip().lower() not in ADMIN_USERNAMES:
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required.")
        
    import subprocess
    import shutil
    
    tools_dir = Path(__file__).resolve().parent.parent.parent / "ShortParse-Tools" / "SpellAudit"
    if not tools_dir.exists():
        tools_dir = Path("/storage/ShortParse-Tools/SpellAudit")
        
    if not tools_dir.exists():
        raise HTTPException(
            status_code=404,
            detail="SpellAudit tools folder not found on this server."
        )
        
    try:
        audit_res = subprocess.run(
            ["python", "audit.py", "--limit-logs", "3", "--boss-count", "2"],
            cwd=str(tools_dir),
            capture_output=True,
            text=True,
            timeout=90
        )
        
        results_dir = tools_dir / "results"
        copied_files = []
        
        if results_dir.exists():
            for class_slug_dir in results_dir.iterdir():
                if class_slug_dir.is_dir():
                    for spec_file in class_slug_dir.iterdir():
                        if spec_file.suffix == ".py":
                            dest_dir = Path(__file__).resolve().parent.parent / "data" / "cooldowns" / class_slug_dir.name
                            dest_dir.mkdir(parents=True, exist_ok=True)
                            
                            with open(spec_file, "r", encoding="utf-8") as sf:
                                draft_content = sf.read()
                                
                            dest_file = dest_dir / f"{spec_file.stem}_discovered.py"
                            with open(dest_file, "w", encoding="utf-8") as df:
                                df.write(draft_content)
                                
                            copied_files.append(f"data/cooldowns/{class_slug_dir.name}/{spec_file.name}")
                            
        if results_dir.exists():
            shutil.rmtree(results_dir)
            
        summary_message = "Successfully ran Cooldowns discovery audit!\n\n"
        if copied_files:
            summary_message += "Discovered and generated new cooldown definition drafts:\n" + "\n".join(f"- {f}" for f in copied_files)
            summary_message += "\n\nDraft modules are saved under data/cooldowns/<class>/<spec>_discovered.py, ready to be reviewed and merged!"
        else:
            summary_message += "No new unmapped player cooldowns were discovered. Your current database is fully up-to-date with top parses!"
            
        return {
            "status": "success",
            "copied_files": copied_files,
            "message": summary_message
        }
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Cooldowns WCL scrape timed out. WCL API might be running slow. Please retry in a moment.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class BannerRequest(BaseModel):
    message: str


@app.get("/banner")
def get_banner(db: Session = Depends(get_db)):
    from shortparse.db_models import SystemConfig
    msg_config = db.query(SystemConfig).filter(SystemConfig.key == "banner_message").first()
    time_config = db.query(SystemConfig).filter(SystemConfig.key == "banner_updated_at").first()
    
    message = msg_config.value if msg_config else None
    updated_at = time_config.value if time_config else None
    
    if message and not message.strip():
        message = None
        
    return {
        "message": message,
        "updated_at": updated_at
    }


@app.post("/admin/banner")
def update_banner(request: Request, payload: BannerRequest, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated.")
        
    from shortparse.settings import ADMIN_USERNAMES
    normalized_username = username.strip().lower()
    if normalized_username not in ADMIN_USERNAMES:
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required.")
        
    from shortparse.db_models import SystemConfig
    
    message = payload.message.strip()
    
    msg_config = db.query(SystemConfig).filter(SystemConfig.key == "banner_message").first()
    if not msg_config:
        msg_config = SystemConfig(key="banner_message", value=message)
        db.add(msg_config)
    else:
        msg_config.value = message
        
    now_str = datetime.utcnow().isoformat()
    time_config = db.query(SystemConfig).filter(SystemConfig.key == "banner_updated_at").first()
    if not time_config:
        time_config = SystemConfig(key="banner_updated_at", value=now_str)
        db.add(time_config)
    else:
        time_config.value = now_str
        
    db.commit()
    
    return {
        "status": "success",
        "message": "Banner updated successfully",
        "banner_message": message if message else None,
        "banner_updated_at": now_str
    }


# Mount static files from ShortParse-Web if directory exists
web_dir = Path(__file__).resolve().parent.parent.parent.parent / "ShortParse-Web"
if not web_dir.exists():
    web_dir = Path(__file__).resolve().parent.parent / "ShortParse-Web"

if web_dir.exists():
    if (web_dir / "css").exists():
        app.mount("/css", StaticFiles(directory=web_dir / "css"), name="css")
    if (web_dir / "js").exists():
        app.mount("/js", StaticFiles(directory=web_dir / "js"), name="js")
    if (web_dir / "images").exists():
        app.mount("/images", StaticFiles(directory=web_dir / "images"), name="images")