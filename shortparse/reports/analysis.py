from shortparse.players import build_roster_from_fight_data

from shortparse.metrics.builder import build_player_metrics
from shortparse.metrics.issues import build_raid_issues
from shortparse.metrics.mechanics import calculate_mechanics
from shortparse.metrics.timeline import build_timeline

from shortparse.benchmarks.builder import build_benchmark_comparisons
from shortparse.reports.scorecard import build_scorecard


def build_fight_analysis(
    report_code: str,
    report_title: str,
    fight: dict,
    fight_data: dict,
    events: list[dict],
) -> dict:

    roster = build_roster_from_fight_data(fight_data)

    fight_duration_seconds = (
        fight["endTime"] - fight["startTime"]
    ) / 1000

    player_metrics = build_player_metrics(
        roster,
        events,
        fight_duration_seconds,
        fight["startTime"],
        fight["endTime"],
        fight["encounterID"],
    )

    mechanics_data = calculate_mechanics(
        roster,
        events,
        fight["encounterID"],
    )

    timeline = build_timeline(
        roster,
        events,
        fight["startTime"],
        fight["endTime"],
        fight["encounterID"],
    )

    benchmark_comparisons = build_benchmark_comparisons(
        report_code,
        fight,
        player_metrics,
    )

    issues = build_raid_issues(
        player_metrics,
        benchmark_comparisons,
    )

    scorecard = build_scorecard(
        player_metrics,
        issues,
        benchmark_comparisons,
    )

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
    }