import os
import json
import concurrent.futures
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from shortparse.database import get_db
from shortparse.db_models import User, Job, LinkedAccount
from shortparse.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/guild", tags=["Guild Suite"])


def require_premium_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Enforces that the user must be logged in and possess an active Patreon Premium status.
    If the user is free, returns a 403 Forbidden exception that the UI can catch.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in with Warcraft Logs before accessing the Guild Suite.",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found.",
        )

    from shortparse.settings import BYPASS_PREMIUM_USERNAMES
    is_bypass = user.username.strip().lower() in BYPASS_PREMIUM_USERNAMES if user.username else False

    if not user.is_premium and not is_bypass:
        raise HTTPException(
            status_code=403,
            detail="The Guild Suite is a Patreon Premium feature. Support us on Patreon to unlock!",
            headers={"X-Premium-Gated": "true"}
        )

    return user


def load_single_analysis_file(result_path: str) -> dict | None:
    """
    Loads and parses a single job analysis JSON file from disk safely.
    """
    try:
        path = Path(result_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
    except Exception as e:
        logger.error("Failed to load analysis JSON file %s: %s", result_path, e)
    return None


def aggregate_guild_history(jobs: list[Job], exclude_list: list[str] | None = None) -> dict:
    """
    Parallelized file-reading aggregator service that processes multiple fight JSONs
    from raw disc storage into a single, cohesive historical dataset.
    """
    # 1. Load result files in parallel using a ThreadPoolExecutor
    result_paths = [job.result_path for job in jobs if job.result_path]
    reports_data = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        results = executor.map(load_single_analysis_file, result_paths)
        for r in results:
            if r:
                reports_data.append(r)

    # Historical metrics containers
    fights_history = []
    player_agg = {}
    progression_killers = {}
    wipe_raw = {}
    total_avoidable_damage_all = 0
    total_fights = 0
    total_overlaps = 0
    total_dry_spells = 0
    all_overlaps_list = []
    all_dry_spells_list = []

    # 2. Iterate through loaded analysis files and compile statistics
    for report in reports_data:
        report_code = report.get("report", {}).get("code", "Unknown")
        report_title = report.get("report", {}).get("title", "Raid Report")
        analyses = report.get("analyses", [])

        for idx, boss_analysis in enumerate(analyses):
            pulls_to_process = boss_analysis.get("pulls_details")
            if not pulls_to_process:
                pulls_to_process = [boss_analysis]

            for pull_analysis in pulls_to_process:
                fight = pull_analysis.get("fight", {})
                scorecard = pull_analysis.get("scorecard", [])
                player_metrics = pull_analysis.get("player_metrics", {})
                mechanics = pull_analysis.get("mechanics", {}).get("raid_mechanics", {})
                defensive_calibrator = pull_analysis.get("defensive_calibrator", {})
                timeline = pull_analysis.get("timeline", [])

                fight_name = fight.get("name", "Unknown")
                is_kill = fight.get("kill", False)
                duration_sec = fight.get("duration_seconds", 0)
                created_at = fight.get("start_time", 0)

                # A. Fight Grade Averages
                grade_points = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
                reverse_points = {5: "S", 4: "A", 3: "B", 2: "C", 1: "D", 0: "F"}
                grades = [grade_points.get(row.get("grade"), 0) for row in scorecard if "grade" in row]
                avg_grade = "C"
                if grades:
                    avg_grade = reverse_points.get(round(sum(grades) / len(grades)), "C")

                # B. Calculate total avoidable damage for this fight
                fight_avoidable_damage = 0
                for player_name, m_data in player_metrics.items():
                    if exclude_list and player_name in exclude_list:
                        continue
                    performance = m_data.get("performance", {})
                    avoidable_dmg = performance.get("avoidable_damage_taken", 0)
                    fight_avoidable_damage += avoidable_dmg

                total_avoidable_damage_all += fight_avoidable_damage
                total_fights += 1

                # Early deaths tracking (< 80% fight duration)
                early_deaths = set()
                for event in timeline:
                    if event.get("type") == "death":
                        dead_player = event.get("target") or event.get("source") or "Unknown"
                        if exclude_list and dead_player in exclude_list:
                            continue
                        event_ts = event.get("timestamp")
                        if event_ts and created_at and duration_sec > 0:
                            elapsed_s = (event_ts - created_at) / 1000
                            if elapsed_s < 0.8 * duration_sec:
                                early_deaths.add(dead_player)

                fights_history.append({
                    "report_code": report_code,
                    "analysis_index": idx,
                    "report_title": report_title,
                    "boss_name": fight_name,
                    "is_kill": is_kill,
                    "avg_grade": avg_grade,
                    "duration_seconds": duration_sec,
                    "avoidable_damage": fight_avoidable_damage,
                    "created_at": created_at,
                })

                # C. Aggregate Player Historical Scorecards
                for row in scorecard:
                    player_name = row.get("player")
                    if not player_name or (exclude_list and player_name in exclude_list):
                        continue

                    # Get fine-tuned metrics from player_metrics
                    metrics_row = player_metrics.get(player_name, {})
                    identity = metrics_row.get("identity", {})
                    performance = metrics_row.get("performance", {})
                    activity = metrics_row.get("activity", {})
                    consumables = metrics_row.get("consumables", {})

                    p_spec = identity.get("spec") or row.get("spec") or metrics_row.get("spec") or "Unknown"
                    p_role = identity.get("role") or row.get("role") or metrics_row.get("role") or "Unknown"
                    p_class = identity.get("class") or row.get("class") or metrics_row.get("class") or "Unknown"

                    if player_name not in player_agg:
                        player_agg[player_name] = {
                            "spec": p_spec,
                            "role": p_role,
                            "class": p_class,
                            "grades": [],
                            "avoidable_damage": [],
                            "dps": [],
                            "hps": [],
                            "deaths": 0,
                            "potions": 0,
                            "healthstones": 0,
                            "low_hp_deaths": 0,
                            "panic_pots_used": 0,
                            "priority_switch_times": [],
                            "priority_switch_dmg": [],
                            "specs_played": set(),
                            "survived_80_count": 0,
                            "player_total_fights": 0,
                        }

                    p_data = player_agg[player_name]
                    
                    # Update spec, role, class if previously "Unknown" and a valid value is found
                    if p_data["spec"] == "Unknown" and p_spec != "Unknown":
                        p_data["spec"] = p_spec
                    if p_data["role"] == "Unknown" and p_role != "Unknown":
                        p_data["role"] = p_role
                    if p_data["class"] == "Unknown" and p_class != "Unknown":
                        p_data["class"] = p_class

                    p_data["grades"].append(row.get("grade", "C"))
                    p_data["specs_played"].add(p_spec)
                    p_data["player_total_fights"] += 1
                    if player_name not in early_deaths:
                        p_data["survived_80_count"] += 1

                    p_data["avoidable_damage"].append(performance.get("avoidable_damage_taken", 0))
                    p_data["dps"].append(performance.get("dps", 0))
                    p_data["hps"].append(performance.get("hps", 0))
                    p_data["deaths"] += performance.get("deaths", 0)
                    p_data["potions"] += consumables.get("combat_potions", 0)
                    p_data["healthstones"] += consumables.get("healthstone_count", 0)

                    # Panic Defensives / Low HP deaths audit
                    if performance.get("deaths", 0) > 0:
                        p_data["low_hp_deaths"] += 1
                        # Check if they used panic defensives/healthstone on death fight
                        if consumables.get("healthstone_count", 0) > 0:
                            p_data["panic_pots_used"] += 1

                    # Priority Target Switch Audit
                    ad_damage = performance.get("priority_ad_damage", 0)
                    switch_time = performance.get("priority_ad_switch_time_sec", 0.0)
                    if ad_damage > 0 or switch_time > 0:
                        p_data["priority_switch_times"].append(switch_time)
                        p_data["priority_switch_dmg"].append(ad_damage)

                # D. Compile "Progression Killer" spell hits on wipes
                if not is_kill:
                    for mech_name, m_data in mechanics.items():
                        hits = m_data.get("hits", 0)
                        damage = m_data.get("damage", 0)
                        if hits > 0:
                            if mech_name not in progression_killers:
                                progression_killers[mech_name] = {
                                    "hits": 0,
                                    "damage": 0,
                                    "fights_count": 0,
                                }
                            progression_killers[mech_name]["hits"] += hits
                            progression_killers[mech_name]["damage"] += damage
                            progression_killers[mech_name]["fights_count"] += 1

                    # E. Compile detailed Wipe Catalyst and Bottleneck metrics
                    if fight_name not in wipe_raw:
                        wipe_raw[fight_name] = {
                            "total_wipes": 0,
                            "hp_list": [],
                            "phase_distribution": {},
                            "hp_distribution": {
                                "100_80": 0,
                                "80_50": 0,
                                "50_20": 0,
                                "20_0": 0
                            },
                            "catalyst_players": {},
                            "catalyst_abilities": {},
                            "death_timestamps": []
                        }
                    
                    w_data = wipe_raw[fight_name]
                    w_data["total_wipes"] += 1
                    
                    # Boss HP tracking
                    boss_hp = fight.get("boss_percentage")
                    if boss_hp is not None:
                        try:
                            hp_val = float(boss_hp)
                            w_data["hp_list"].append(hp_val)
                            if hp_val >= 80:
                                w_data["hp_distribution"]["100_80"] += 1
                            elif hp_val >= 50:
                                w_data["hp_distribution"]["80_50"] += 1
                            elif hp_val >= 20:
                                w_data["hp_distribution"]["50_20"] += 1
                            else:
                                w_data["hp_distribution"]["20_0"] += 1
                        except Exception:
                            pass
                    
                    # Phase tracking
                    phase = fight.get("phase")
                    if phase is not None:
                        try:
                            phase_num = int(phase)
                            phase_name = f"Phase {phase_num + 1}"
                        except Exception:
                            phase_name = str(phase) if str(phase).startswith("Phase") else f"Phase {phase}"
                        w_data["phase_distribution"][phase_name] = w_data["phase_distribution"].get(phase_name, 0) + 1
                    
                    # Find first death catalyst
                    for event in timeline:
                        if event.get("type") == "death":
                            dead_player = event.get("target") or event.get("source") or "Unknown"
                            ability = event.get("spell_name") or "Unknown"
                            time_str = event.get("time") or "00:00"
                            
                            w_data["catalyst_players"][dead_player] = w_data["catalyst_players"].get(dead_player, 0) + 1
                            w_data["catalyst_abilities"][ability] = w_data["catalyst_abilities"].get(ability, 0) + 1
                            
                            try:
                                parts = time_str.split(":")
                                if len(parts) == 2:
                                    w_data["death_timestamps"].append(int(parts[0]) * 60 + int(parts[1]))
                            except Exception:
                                pass
                            break

                # F. Healer audit overlap and dry spell aggregation
                overlaps = defensive_calibrator.get("overlaps", []) if isinstance(defensive_calibrator, dict) else []
                dry_spells = defensive_calibrator.get("dry_spells", []) if isinstance(defensive_calibrator, dict) else []
                total_overlaps += len(overlaps)
                total_dry_spells += len(dry_spells)
                for o in overlaps:
                    all_overlaps_list.append({
                        "boss_name": fight_name,
                        "time_range": o.get("time_range"),
                        "summary": f"[{fight_name}] {o.get('summary')}"
                    })
                for d in dry_spells:
                    all_dry_spells_list.append({
                        "boss_name": fight_name,
                        "time_range": d.get("time_range"),
                        "summary": f"[{fight_name}] {d.get('summary')}"
                    })

    # 3. Format Consolidated Player Historical scorecards & Ledgers
    formatted_players = {}
    for player_name, p_data in player_agg.items():
        avg_grades = p_data["grades"]
        grades_nums = [grade_points.get(g, 0) for g in avg_grades]
        player_avg_grade = reverse_points.get(round(sum(grades_nums) / len(grades_nums)), "C") if grades_nums else "C"

        avg_avoidable = sum(p_data["avoidable_damage"]) / len(p_data["avoidable_damage"]) if p_data["avoidable_damage"] else 0
        avg_dps = sum(p_data["dps"]) / len(p_data["dps"]) if p_data["dps"] else 0
        avg_hps = sum(p_data["hps"]) / len(p_data["hps"]) if p_data["hps"] else 0

        # Survival quadrants calculation (X = DPS/HPS relative, Y = Avoidable Damage inverse)
        # Avoidable damage benchmark is set around 1M. Lower is better.
        survival_score = max(0, min(100, int(100 - (avg_avoidable / 40000))))

        # Consumable Panic Button Audit
        low_hp_deaths = p_data["low_hp_deaths"]
        panic_pct = 100
        if low_hp_deaths > 0:
            panic_pct = int((p_data["panic_pots_used"] / low_hp_deaths) * 100)

        # Priority Switch Averages
        avg_switch_time = sum(p_data["priority_switch_times"]) / len(p_data["priority_switch_times"]) if p_data["priority_switch_times"] else 1.5
        avg_switch_dmg = sum(p_data["priority_switch_dmg"]) / len(p_data["priority_switch_dmg"]) if p_data["priority_switch_dmg"] else 0

        # Gold Repair Debt: 100g per 1M avoidable damage
        gold_debt = int(sum(p_data["avoidable_damage"]) / 10000)

        # Calculate URS (Uptime Reliability Score) - % of fights they survived past 80% mark
        urs = 100
        if p_data.get("player_total_fights", 0) > 0:
            urs = int((p_data["survived_80_count"] / p_data["player_total_fights"]) * 100)

        # Calculate SPI (Survival-to-Performance Index) - combines output and survival
        output_val = avg_dps if p_data["role"] == "DPS" else avg_hps
        perf_factor = output_val / 20000.0
        dmg_penalty = avg_avoidable / 20000.0
        spi = max(10, min(100, int(50 + (perf_factor * 10) - (dmg_penalty * 15))))

        specs_played = list(p_data.get("specs_played", set()))
        if "Unknown" in specs_played and len(specs_played) > 1:
            specs_played.remove("Unknown")
        if not specs_played or (len(specs_played) == 1 and specs_played[0] == "Unknown" and p_data["spec"] != "Unknown"):
            specs_played = [p_data["spec"]]
        is_flex = len(specs_played) > 1

        formatted_players[player_name] = {
            "spec": p_data["spec"],
            "role": p_data["role"],
            "class": p_data.get("class", "Unknown"),
            "fights_count": len(avg_grades),
            "avg_grade": player_avg_grade,
            "avg_avoidable_damage": int(avg_avoidable),
            "avg_dps": int(avg_dps),
            "avg_hps": int(avg_hps),
            "total_deaths": p_data["deaths"],
            "survival_score": survival_score,
            "panic_healthstone_pct": panic_pct,
            "avg_priority_switch_time_sec": round(avg_switch_time, 2),
            "avg_priority_switch_dmg": int(avg_switch_dmg),
            "gold_debt": gold_debt,
            "urs": urs,
            "spi": spi,
            "specs_played": specs_played,
            "is_flex": is_flex,
        }

    # 4. Generate Roster Buff & Synergy Audit (Uses latest fight roster)
    active_buffs = []
    missing_buffs = []
    buff_synergy_details = []
    
    if reports_data:
        latest_report = reports_data[0] # Fights are ordered by created_at desc
        latest_roster = latest_report.get("roster")
        if not latest_roster:
            analyses = latest_report.get("analyses", [])
            if analyses:
                latest_roster = analyses[0].get("roster", [])
            else:
                latest_roster = []
        
        # Check roster specs for synergy buffs
        has_warrior = any(p.get("class") == "Warrior" for p in latest_roster)
        has_mage = any(p.get("class") == "Mage" for p in latest_roster)
        has_druid = any(p.get("class") == "Druid" for p in latest_roster)
        has_dh = any(p.get("class") == "DemonHunter" or p.get("class") == "Demon Hunter" for p in latest_roster)
        has_monk = any(p.get("class") == "Monk" for p in latest_roster)
        has_priest = any(p.get("class") == "Priest" for p in latest_roster)

        # Compile buffs
        if has_warrior:
            active_buffs.append("Battle Shout (5% Attack Power)")
        else:
            missing_buffs.append("Battle Shout")
            buff_synergy_details.append({
                "buff": "Battle Shout",
                "class": "Warrior",
                "benefit": "Increases attack power by 5% for all physical damage dealers.",
            })

        if has_mage:
            active_buffs.append("Arcane Intellect (5% Intellect)")
        else:
            missing_buffs.append("Arcane Intellect")
            buff_synergy_details.append({
                "buff": "Arcane Intellect",
                "class": "Mage",
                "benefit": "Increases Intellect by 5% for all mana users and spell casters.",
            })

        if has_druid:
            active_buffs.append("Mark of the Wild (3% Versatility)")
        else:
            missing_buffs.append("Mark of the Wild")
            buff_synergy_details.append({
                "buff": "Mark of the Wild",
                "class": "Druid",
                "benefit": "Increases Versatility by 3% for the entire raid group.",
            })

        if has_dh:
            active_buffs.append("Chaos Brand (5% Magic Damage)")
        else:
            missing_buffs.append("Chaos Brand")
            buff_synergy_details.append({
                "buff": "Chaos Brand",
                "class": "Demon Hunter",
                "benefit": "Applies Chaos Brand to targets, increasing magic damage taken by 5%.",
            })

        if has_monk:
            active_buffs.append("Generous Pour & Mystic Touch (5% Physical Damage)")
        else:
            missing_buffs.append("Mystic Touch")
            buff_synergy_details.append({
                "buff": "Mystic Touch",
                "class": "Monk",
                "benefit": "Applies Mystic Touch to targets, increasing physical damage taken by 5%.",
            })

        if has_priest:
            active_buffs.append("Power Word: Fortitude (5% Stamina)")
        else:
            missing_buffs.append("Power Word: Fortitude")
            buff_synergy_details.append({
                "buff": "Power Word: Fortitude",
                "class": "Priest",
                "benefit": "Increases Stamina by 5% for all raid group members.",
            })

    # Sort histories
    fights_history.sort(key=lambda x: x["created_at"])

    # Format completed wipe statistics per boss
    wipe_analytics = {}
    for boss_name, raw in wipe_raw.items():
        avg_hp = round(sum(raw["hp_list"]) / len(raw["hp_list"]), 1) if raw["hp_list"] else 0.0
        
        sorted_players = [
            {"player": name, "count": count}
            for name, count in sorted(raw["catalyst_players"].items(), key=lambda x: x[1], reverse=True)
        ]
        sorted_abilities = [
            {"ability": name, "count": count}
            for name, count in sorted(raw["catalyst_abilities"].items(), key=lambda x: x[1], reverse=True)
        ]
        
        wipe_analytics[boss_name] = {
            "total_wipes": raw["total_wipes"],
            "avg_boss_hp": avg_hp,
            "phase_distribution": raw["phase_distribution"],
            "hp_distribution": raw["hp_distribution"],
            "catalyst_players": sorted_players,
            "catalyst_abilities": sorted_abilities,
            "death_timestamps": sorted(raw["death_timestamps"])
        }

    return {
        "guild_averages": {
            "total_fights_analyzed": total_fights,
            "average_avoidable_damage": int(total_avoidable_damage_all / total_fights) if total_fights > 0 else 0,
        },
        "fights_history": fights_history,
        "players_history": formatted_players,
        "progression_killers": progression_killers,
        "synergy_buffs": {
            "active": active_buffs,
            "missing": missing_buffs,
            "suggestions": buff_synergy_details,
        },
        "wipe_analytics": wipe_analytics,
        "healer_audit": {
            "total_overlaps": total_overlaps,
            "total_dry_spells": total_dry_spells,
            "recent_overlaps": all_overlaps_list[:10],
            "recent_dry_spells": all_dry_spells_list[:10]
        }
    }


@router.get("/overview")
def get_guild_suite_overview(
    db: Session = Depends(get_db),
    user: User = Depends(require_premium_user),
):
    """
    Returns the complete aggregated historical Guild Suite analytics dataset.
    This endpoint is strictly gated under Patreon Premium checks.
    """
    logger.info("Premium Guild Suite overview requested by user: %s", user.username)

    # 1. Find all completed jobs for this user (max 50 to keep processing fast)
    completed_jobs = db.query(Job).filter(
        Job.user_id == user.id,
        Job.status == "completed",
    ).order_by(Job.created_at.desc()).limit(50).all()

    if not completed_jobs:
        return {
            "guild_averages": {
                "total_fights_analyzed": 0,
                "average_avoidable_damage": 0,
            },
            "fights_history": [],
            "players_history": {},
            "progression_killers": {},
            "synergy_buffs": {
                "active": [],
                "missing": [],
                "suggestions": [],
            },
            "excluded_players": user.excluded_ledger_players or []
        }

    # 2. Compile and return aggregated historical analytics
    res = aggregate_guild_history(completed_jobs, exclude_list=user.excluded_ledger_players)
    res["excluded_players"] = user.excluded_ledger_players or []
    return res


@router.get("/mrt-notes")
def get_mrt_notes(
    job_id: str,
    analysis_index: int = 0,
    db: Session = Depends(get_db),
    user: User = Depends(require_premium_user),
):
    """
    Generates copy-pasteable Method Raid Tools (MRT) or Angry Assignments notes
    matching boss mechanics / spikes to player cooldowns from the active roster.
    """
    logger.info("Premium MRT notes requested by user %s for job %s", user.username, job_id)
    
    # 1. Fetch the job from DB
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    result_path = job.result_path
    if not result_path:
        raise HTTPException(status_code=400, detail="Job results are not available yet.")
        
    # 2. Load the analysis JSON from disk
    analysis_data = load_single_analysis_file(result_path)
    if not analysis_data:
        raise HTTPException(status_code=500, detail="Failed to load job analysis data.")
        
    analyses = analysis_data.get("analyses", [])
    if not analyses:
        raise HTTPException(status_code=404, detail="No analyses found in this job.")
        
    idx = max(0, min(analysis_index, len(analyses) - 1))
    analysis = analyses[idx]
    
    roster = analysis.get("roster", [])
    defensive_calibrator = analysis.get("defensive_calibrator", {})
    spikes = defensive_calibrator.get("spikes", [])
    
    # 3. Import and call the notes generator
    from shortparse.server.mrt_builder import generate_mrt_notes
    notes = generate_mrt_notes(roster, spikes)
    
    return {"notes": notes}


@router.get("/roster-calibrator")
def get_roster_calibrator(
    db: Session = Depends(get_db),
    user: User = Depends(require_premium_user),
):
    """
    Returns the Smart Bench & Flex Spec calibrator dataset.
    Identifies flex spec candidates and recommends roster optimizations.
    """
    logger.info("Premium roster-calibrator requested by user: %s", user.username)

    completed_jobs = db.query(Job).filter(
        Job.user_id == user.id,
        Job.status == "completed",
    ).order_by(Job.created_at.desc()).limit(50).all()

    if not completed_jobs:
        return {"flex_recommendations": [], "roster_bench_grades": {}}

    history = aggregate_guild_history(completed_jobs, exclude_list=user.excluded_ledger_players)
    players_history = history.get("players_history", {})

    # Flex recommendations algorithm
    flex_recommendations = []
    
    # Roster mapping for potential spec flex
    FLEX_SPECS_MAP = {
        "Priest": ["Holy", "Discipline", "Shadow"],
        "Paladin": ["Holy", "Protection", "Retribution"],
        "Druid": ["Restoration", "Guardian", "Feral", "Balance"],
        "Shaman": ["Restoration", "Elemental", "Enhancement"],
        "Monk": ["Mistweaver", "Brewmaster", "Windwalker"],
        "Death Knight": ["Blood", "Frost", "Unholy"],
        "Deathknight": ["Blood", "Frost", "Unholy"],
        "Demon Hunter": ["Vengeance", "Havoc"],
        "Demonhunter": ["Vengeance", "Havoc"],
        "Warrior": ["Protection", "Arms", "Fury"],
    }

    for name, p in players_history.items():
        specs_played = p.get("specs_played", [])
        
        # Determine class from active spec if possible
        detected_class = "Unknown"
        for class_name, specs in FLEX_SPECS_MAP.items():
            for sp in specs:
                if sp.lower() in p["spec"].lower():
                    detected_class = class_name
                    break
            if detected_class != "Unknown":
                break

        potential_specs = FLEX_SPECS_MAP.get(detected_class, [])
        other_potential = [s for s in potential_specs if s.lower() not in [sp.lower() for sp in specs_played]]

        if len(specs_played) > 1 or other_potential:
            flex_recommendations.append({
                "player": name,
                "class": detected_class,
                "current_spec": p["spec"],
                "specs_played": specs_played,
                "potential_specs": other_potential,
                "spi": p["spi"],
                "urs": p["urs"],
                "survival_score": p["survival_score"],
                "efficiency_rating": p["spi"] + 5 if p["urs"] > 85 else p["spi"] - 10
            })

    # Sort flex recommendations by efficiency rating
    flex_recommendations.sort(key=lambda x: x["efficiency_rating"], reverse=True)

    return {
        "flex_recommendations": flex_recommendations,
        "roster_bench_grades": players_history
    }


from pydantic import BaseModel

class CoachChatRequest(BaseModel):
    job_id: str
    analysis_index: int = 0
    pull_index: str = "all"
    message: str


@router.post("/coach-chat")
def post_coach_chat(
    payload: CoachChatRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Raid Coach Conversational AI log analyzer.
    Gated behind Patreon Premium user authentication check OR user's own Gemini API key.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in with Warcraft Logs before accessing the AI Coach.",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found.",
        )

    from shortparse.settings import BYPASS_PREMIUM_USERNAMES
    is_bypass = user.username.strip().lower() in BYPASS_PREMIUM_USERNAMES if user.username else False
    is_premium = user.is_premium or is_bypass
    
    has_own_key = bool(user.gemini_api_key and user.gemini_api_key.strip())

    if not is_premium and not has_own_key:
        raise HTTPException(
            status_code=403,
            detail="The Raid Coach AI Chat is a Patreon Premium feature. Support us on Patreon or provide your own Gemini API Key in Settings to unlock!",
            headers={"X-Premium-Gated": "true"}
        )

    logger.info("Raid Coach AI query from user %s for job %s: %s", user.username, payload.job_id, payload.message)
    
    # 1. Fetch the job from DB
    job = db.query(Job).filter(Job.job_id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    result_path = job.result_path
    if not result_path:
        raise HTTPException(status_code=400, detail="Job results are not available yet.")
        
    # 2. Load the analysis JSON from disk
    analysis_data = load_single_analysis_file(result_path)
    if not analysis_data:
        raise HTTPException(status_code=500, detail="Failed to load job analysis data.")
        
    analyses = analysis_data.get("analyses", [])
    if not analyses:
        raise HTTPException(status_code=404, detail="No analyses found in this job.")
        
    idx = max(0, min(payload.analysis_index, len(analyses) - 1))
    analysis = analyses[idx]
    
    # 3. Query the Gemini AI Coach engine
    from shortparse.server.ai_coach import ask_gemini_coach
    reply = ask_gemini_coach(payload.message, analysis, custom_key=user.gemini_api_key, pull_index=payload.pull_index)
    
    return {"reply": reply}


class ExcludePlayersRequest(BaseModel):
    players: list[str]


@router.post("/exclude-players")
def post_exclude_players(
    payload: ExcludePlayersRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_premium_user),
):
    """
    Excludes specific players from the guild suite ledger and roster matrix.
    """
    logger.info("Excluding players from ledger for user %s: %s", user.username, payload.players)
    current_excluded = user.excluded_ledger_players or []
    new_excluded = list(set(current_excluded + payload.players))
    user.excluded_ledger_players = new_excluded
    db.commit()
    return {"status": "success", "excluded": new_excluded}


class RestorePlayersRequest(BaseModel):
    players: list[str]


@router.post("/restore-players")
def post_restore_players(
    payload: RestorePlayersRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_premium_user),
):
    """
    Restores previously excluded players back to the ledger and roster matrix.
    """
    logger.info("Restoring players to ledger for user %s: %s", user.username, payload.players)
    current_excluded = user.excluded_ledger_players or []
    new_excluded = [p for p in current_excluded if p not in payload.players]
    user.excluded_ledger_players = new_excluded
    db.commit()
    return {"status": "success", "excluded": new_excluded}




