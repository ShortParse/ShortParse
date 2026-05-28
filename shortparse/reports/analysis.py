from shortparse.players import build_roster_from_fight_data

from shortparse.metrics.builder import build_player_metrics
from shortparse.metrics.issues import build_raid_issues
from shortparse.metrics.mechanics import calculate_mechanics
from shortparse.metrics.timeline import build_timeline

from shortparse.benchmarks.builder import build_benchmark_comparisons
from shortparse.reports.scorecard import build_scorecard

from shortparse.reports.coach.summary import build_raid_coach_summary
from shortparse.metrics.calibrator import calculate_defensive_calibrator

def build_fight_analysis(
    report_code: str,
    report_title: str,
    fight: dict,
    fight_data: dict,
    events: list[dict],
    progress_callback=None,
) -> dict:

    def progress(message: str) -> None:
        if progress_callback:
            progress_callback(message)

    progress("building roster...")

    roster = build_roster_from_fight_data(fight_data)

    damage_taken_table = fight_data.get("damageTaken", {})

    fight_duration_seconds = (
        fight["endTime"] - fight["startTime"]
    ) / 1000

    progress("calculating player metrics...")

    player_metrics = build_player_metrics(
        roster,
        events,
        damage_taken_table,
        fight_duration_seconds,
        fight["startTime"],
        fight["endTime"],
        fight["encounterID"],
        fight_data=fight_data,
    )

    progress("calculating tracked mechanics...")

    mechanics_data = calculate_mechanics(
        roster,
        events,
        fight["encounterID"],
    )

    progress("building fight timeline...")

    timeline = build_timeline(
        roster,
        events,
        fight["startTime"],
        fight["endTime"],
        fight["encounterID"],
    )

    progress("comparing players against benchmarks...")

    benchmark_comparisons = build_benchmark_comparisons(
        report_code,
        fight,
        player_metrics,
        progress_callback=progress,
    )

    progress("building raid issues...")

    issues = build_raid_issues(
        player_metrics,
        benchmark_comparisons,
    )

    progress("building scorecard...")

    scorecard = build_scorecard(
        player_metrics,
        issues,
        benchmark_comparisons,
    )

    progress("building raid coach summary...")

    raid_coach = build_raid_coach_summary(
        fight=fight,
        roster=roster,
        player_metrics=player_metrics,
        mechanics=mechanics_data,
        benchmarks=benchmark_comparisons,
        issues=issues,
        scorecard=scorecard,
    )

    progress("calculating defensive CD calibration...")

    defensive_calibrator = calculate_defensive_calibrator(
        fight=fight,
        events=events,
        roster=roster,
        fight_data=fight_data,
    )

    progress("fight analysis complete.")

    return {
        "report": {
            "code": report_code,
            "title": report_title,
        },
        "fight": {
            "id": fight["id"],
            "name": fight.get("name", "Unknown"),
            "encounter_id": fight.get("encounterID"),
            "difficulty": fight.get("difficulty"),
            "kill": fight.get("kill", False),
            "start_time": fight["startTime"],
            "end_time": fight["endTime"],
            "duration_seconds": fight_duration_seconds,
            "boss_percentage": fight.get("bossPercentage"),
            "fight_percentage": fight.get("fightPercentage"),
            "phase": fight.get("lastPhaseAsAbsoluteIndex"),
        },
        "roster": roster,
        "player_metrics": player_metrics,
        "mechanics": mechanics_data,
        "timeline": timeline,
        "benchmarks": benchmark_comparisons,
        "issues": issues,
        "scorecard": scorecard,
        "raid_coach": raid_coach,
        "defensive_calibrator": defensive_calibrator,
    }


def average_grade(grades: list[str]) -> str:
    grade_points = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
    reverse_points = {5: "S", 4: "A", 3: "B", 2: "C", 1: "D", 0: "F"}
    points = [grade_points.get(g, 2) for g in grades if g in grade_points]
    if not points:
        return "C"
    avg = round(sum(points) / len(points))
    return reverse_points.get(avg, "C")


def aggregate_pull_analyses(
    pull_analyses: list[dict],
    report_code: str,
    report_title: str,
) -> dict:
    if not pull_analyses:
        return {}

    # 1. Identify the "best" fight based on kill status or progress score
    kills = [a for a in pull_analyses if a["fight"]["kill"]]
    if kills:
        best_analysis = sorted(kills, key=lambda a: a["fight"]["end_time"])[-1]
    else:
        def get_analysis_progress(a):
            f = a["fight"]
            absolute_phase = f.get("phase") or 0
            fight_percentage = f.get("fight_percentage") or 100.0
            progress = 100.0 - fight_percentage
            duration = f.get("duration_seconds") or 0
            return (absolute_phase, progress, duration)
        best_analysis = max(pull_analyses, key=get_analysis_progress)

    best_fight = best_analysis["fight"]

    # Build primary aggregated fight metadata
    aggregated_fight = {
        "id": best_fight["id"],
        "name": best_fight.get("name", "Unknown"),
        "encounter_id": best_fight.get("encounter_id"),
        "difficulty": best_fight.get("difficulty"),
        "kill": len(kills) > 0,
        "start_time": best_fight["start_time"],
        "end_time": best_fight["end_time"],
        "duration_seconds": sum(a["fight"]["duration_seconds"] for a in pull_analyses) / len(pull_analyses),
        "boss_percentage": min((a["fight"].get("boss_percentage") for a in pull_analyses if a["fight"].get("boss_percentage") is not None), default=best_fight.get("boss_percentage")),
        "fight_percentage": min((a["fight"].get("fight_percentage") for a in pull_analyses if a["fight"].get("fight_percentage") is not None), default=best_fight.get("fight_percentage")),
        "phase": max((a["fight"].get("phase") for a in pull_analyses if a["fight"].get("phase") is not None), default=best_fight.get("phase")),
        "total_pulls": len(pull_analyses),
        "kills_count": len(kills),
        "wipes_count": len(pull_analyses) - len(kills),
        "is_aggregated": True,
    }

    # 2. Merge roster across all pulls
    roster_by_name = {}
    for a in pull_analyses:
        for p in a.get("roster", []):
            name = p.get("name")
            if not name:
                continue
            if name not in roster_by_name:
                roster_by_name[name] = p.copy()
    roster = list(roster_by_name.values())

    # 3. Aggregate player metrics
    aggregated_player_metrics = {}
    # Find all unique players mentioned in player_metrics of any pull
    all_players = set()
    for a in pull_analyses:
        all_players.update(a.get("player_metrics", {}).keys())

    for player_name in all_players:
        # Gather metrics across the pulls this player participated in
        player_pulls = []
        for a in pull_analyses:
            p_metrics = a.get("player_metrics", {}).get(player_name)
            if p_metrics:
                player_pulls.append(p_metrics)

        if not player_pulls:
            continue

        # Extract base identity
        base_pm = player_pulls[0]
        p_class = base_pm.get("class", "Unknown")
        p_spec = base_pm.get("spec", "Unknown")
        p_role = base_pm.get("role", "Unknown")

        # Sum or average fields
        dps_list = [p.get("performance", {}).get("dps", 0) for p in player_pulls]
        hps_list = [p.get("performance", {}).get("hps", 0) for p in player_pulls]
        active_list = [p.get("activity", {}).get("active_percentage", 95.0) for p in player_pulls]
        avoidable_dmg_list = [p.get("performance", {}).get("avoidable_damage_taken", 0) for p in player_pulls]
        avoidable_hits_list = [p.get("performance", {}).get("avoidable_mechanic_hits", 0) for p in player_pulls]
        potions_list = [p.get("consumables", {}).get("combat_potions", 0) for p in player_pulls]
        hs_list = [p.get("consumables", {}).get("healthstone_count", 0) for p in player_pulls]
        
        deaths_sum = sum(p.get("performance", {}).get("deaths", 0) for p in player_pulls)

        avg_dps = sum(dps_list) / len(dps_list) if dps_list else 0
        avg_hps = sum(hps_list) / len(hps_list) if hps_list else 0
        avg_active = sum(active_list) / len(active_list) if active_list else 95.0
        avg_avoidable_dmg = sum(avoidable_dmg_list) / len(avoidable_dmg_list) if avoidable_dmg_list else 0
        avg_avoidable_hits = sum(avoidable_hits_list) / len(avoidable_hits_list) if avoidable_hits_list else 0
        avg_potions = sum(potions_list) / len(potions_list) if potions_list else 0
        avg_hs = sum(hs_list) / len(hs_list) if hs_list else 0

        # Maintain priority target switch metrics
        ad_dmg_list = [p.get("performance", {}).get("priority_ad_damage", 0) for p in player_pulls]
        switch_time_list = [p.get("performance", {}).get("priority_ad_switch_time_sec", 0.0) for p in player_pulls]
        avg_ad_dmg = sum(ad_dmg_list) / len(ad_dmg_list) if ad_dmg_list else 0
        avg_switch_time = sum(switch_time_list) / len(switch_time_list) if switch_time_list else 0.0

        aggregated_player_metrics[player_name] = {
            "class": p_class,
            "spec": p_spec,
            "role": p_role,
            "performance": {
                "dps": int(avg_dps),
                "hps": int(avg_hps),
                "deaths": deaths_sum,
                "avoidable_damage_taken": int(avg_avoidable_dmg),
                "avoidable_mechanic_hits": int(avg_avoidable_hits),
                "priority_ad_damage": int(avg_ad_dmg),
                "priority_ad_switch_time_sec": round(avg_switch_time, 2),
            },
            "activity": {
                "active_percentage": round(avg_active, 1)
            },
            "consumables": {
                "combat_potions": round(avg_potions, 1),
                "healthstone_count": round(avg_hs, 1),
            }
        }

    # 4. Merge mechanics
    aggregated_player_mechanics = {}
    aggregated_raid_mechanics = {}

    for a in pull_analyses:
        mech_data = a.get("mechanics", {})
        
        # Merge player mechanics
        for player_name, p_mechs in mech_data.get("player_mechanics", {}).items():
            if player_name not in aggregated_player_mechanics:
                aggregated_player_mechanics[player_name] = {}
            for mech_name, m_data in p_mechs.items():
                if mech_name not in aggregated_player_mechanics[player_name]:
                    aggregated_player_mechanics[player_name][mech_name] = {
                        "hits": [],
                        "damage": []
                    }
                aggregated_player_mechanics[player_name][mech_name]["hits"].append(m_data.get("hits", 0))
                aggregated_player_mechanics[player_name][mech_name]["damage"].append(m_data.get("damage", 0))

        # Merge raid mechanics
        for mech_name, m_data in mech_data.get("raid_mechanics", {}).items():
            if mech_name not in aggregated_raid_mechanics:
                aggregated_raid_mechanics[mech_name] = {
                    "hits": [],
                    "damage": [],
                    "description": m_data.get("description", ""),
                    "players": {}
                }
            aggregated_raid_mechanics[mech_name]["hits"].append(m_data.get("hits", 0))
            aggregated_raid_mechanics[mech_name]["damage"].append(m_data.get("damage", 0))
            
            # Players list per mechanic
            for p_hit in m_data.get("players_hit", []):
                aggregated_raid_mechanics[mech_name]["players"][p_hit] = True

    # Finalize averaged mechanics
    num_pulls = len(pull_analyses)
    player_mechanics = {}
    for p_name, mechs in aggregated_player_mechanics.items():
        player_mechanics[p_name] = {}
        for m_name, lists in mechs.items():
            # Pad lists with zeros for pulls where they had 0 hits
            hits_padded = lists["hits"] + [0] * (num_pulls - len(lists["hits"]))
            dmg_padded = lists["damage"] + [0] * (num_pulls - len(lists["damage"]))
            player_mechanics[p_name][m_name] = {
                "hits": int(sum(hits_padded) / num_pulls),
                "damage": int(sum(dmg_padded) / num_pulls)
            }

    raid_mechanics = {}
    for m_name, data in aggregated_raid_mechanics.items():
        hits_padded = data["hits"] + [0] * (num_pulls - len(data["hits"]))
        dmg_padded = data["damage"] + [0] * (num_pulls - len(data["damage"]))
        
        # Worst player hits calculation over all pulls combined
        worst_player = "None"
        worst_hits = 0
        for p_name in data["players"]:
            p_pulls_hits = [
                a.get("mechanics", {}).get("player_mechanics", {}).get(p_name, {}).get(m_name, {}).get("hits", 0)
                for a in pull_analyses
            ]
            avg_p_hits = sum(p_pulls_hits) / num_pulls
            if avg_p_hits > worst_hits:
                worst_hits = avg_p_hits
                worst_player = p_name

        raid_mechanics[m_name] = {
            "hits": int(sum(hits_padded) / num_pulls),
            "damage": int(sum(dmg_padded) / num_pulls),
            "description": data["description"],
            "worst_player": worst_player,
            "worst_hits": round(worst_hits, 1),
            "players_hit": list(data["players"].keys())
        }

    mechanics = {
        "player_mechanics": player_mechanics,
        "raid_mechanics": raid_mechanics
    }

    # 5. Aggregate scorecard
    # We rebuild the scorecard using aggregated averages!
    scorecard = []
    for player_name, p_metrics in aggregated_player_metrics.items():
        # Find their grades across all pulls in which they participated
        player_grades = []
        for a in pull_analyses:
            sc_row = next((r for r in a.get("scorecard", []) if r.get("player") == player_name), None)
            if sc_row:
                player_grades.append(sc_row.get("grade", "C"))
                
        avg_g = average_grade(player_grades)
        
        scorecard.append({
            "player": player_name,
            "spec": p_metrics["spec"],
            "role": p_metrics["role"],
            "grade": avg_g,
            "dps": p_metrics["performance"]["dps"],
            "hps": p_metrics["performance"]["hps"],
            "avoidable_damage": p_metrics["performance"]["avoidable_damage_taken"],
        })

    # Sort scorecard by grade descending or by name
    grade_points = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
    scorecard.sort(key=lambda r: (-grade_points.get(r["grade"], 2), r["player"]))

    # 6. Fallback items from best analysis
    timeline = best_analysis.get("timeline", [])
    benchmarks = best_analysis.get("benchmarks", [])
    issues = best_analysis.get("issues", [])
    raid_coach = best_analysis.get("raid_coach", {})
    defensive_calibrator = best_analysis.get("defensive_calibrator", {})

    # Save pulls_details
    pulls_details = []
    for idx, a in enumerate(pull_analyses, start=1):
        pull_copy = a.copy()
        pull_copy["fight"] = a["fight"].copy()
        pull_copy["fight"]["pull_number"] = idx
        pulls_details.append(pull_copy)

    return {
        "report": {
            "code": report_code,
            "title": report_title,
        },
        "fight": aggregated_fight,
        "roster": roster,
        "player_metrics": aggregated_player_metrics,
        "mechanics": mechanics,
        "timeline": timeline,
        "benchmarks": benchmarks,
        "issues": issues,
        "scorecard": scorecard,
        "raid_coach": raid_coach,
        "defensive_calibrator": defensive_calibrator,
        "pulls_details": pulls_details,
    }