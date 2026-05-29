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
    raids_dirs = ["the_voidspire", "the_dreamrift", "march_on_queldanas"]
    
    result = []
    
    for raid_id in raids_dirs:
        raid_path = base_dir / raid_id
        if not raid_path.is_dir():
            continue
            
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
    from shortparse.settings import REDIS_HOST, REDIS_PORT, DB_PATH
    
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