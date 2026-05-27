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