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

    if not user.is_premium:
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


def aggregate_guild_history(jobs: list[Job]) -> dict:
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

    # 2. Iterate through loaded analysis files and compile statistics
    for report in reports_data:
        report_code = report.get("report", {}).get("code", "Unknown")
        report_title = report.get("report", {}).get("title", "Raid Report")
        analyses = report.get("analyses", [])

        for idx, analysis in enumerate(analyses):
            fight = analysis.get("fight", {})
            scorecard = analysis.get("scorecard", [])
            player_metrics = analysis.get("player_metrics", {})
            mechanics = analysis.get("mechanics", {}).get("raid_mechanics", {})
            defensive_calibrator = analysis.get("defensive_calibrator", {})

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
                performance = m_data.get("performance", {})
                avoidable_dmg = performance.get("avoidable_damage_taken", 0)
                fight_avoidable_damage += avoidable_dmg

            total_avoidable_damage_all += fight_avoidable_damage
            total_fights += 1

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
                if not player_name:
                    continue

                if player_name not in player_agg:
                    player_agg[player_name] = {
                        "spec": row.get("spec", "Unknown"),
                        "role": row.get("role", "Unknown"),
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
                    }

                p_data = player_agg[player_name]
                p_data["grades"].append(row.get("grade", "C"))

                # Get fine-tuned metrics from player_metrics
                metrics_row = player_metrics.get(player_name, {})
                performance = metrics_row.get("performance", {})
                activity = metrics_row.get("activity", {})
                consumables = metrics_row.get("consumables", {})

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
                timeline = analysis.get("timeline", [])
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

        formatted_players[player_name] = {
            "spec": p_data["spec"],
            "role": p_data["role"],
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
        }

    # 4. Generate Roster Buff & Synergy Audit (Uses latest fight roster)
    active_buffs = []
    missing_buffs = []
    buff_synergy_details = []
    
    if reports_data:
        latest_report = reports_data[0] # Fights are ordered by created_at desc
        latest_roster = latest_report.get("roster", [])
        
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
        "wipe_analytics": wipe_analytics
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
            }
        }

    # 2. Compile and return aggregated historical analytics
    return aggregate_guild_history(completed_jobs)
