SEVERITY_COLUMNS = {
    "Critical": "critical_count",
    "Major": "major_count",
    "Warning": "warning_count",
    "Info": "info_count",
}


def get_default_scorecard_row(
    player_name: str,
    benchmark_grade: str = "N/A",
) -> dict:
    return {
        "player": player_name,
        "grade": benchmark_grade,
        "issue_score": 0,
        "critical_count": 0,
        "major_count": 0,
        "warning_count": 0,
        "info_count": 0,
        "top_issue": "",
    }


def build_scorecard(
    player_metrics: dict,
    issues: list[dict],
    benchmark_comparisons: dict,
) -> list[dict]:
    rows = {}

    for player_name in player_metrics:
        comparison = benchmark_comparisons.get(player_name)
        grade = comparison.grade if comparison else "N/A"

        rows[player_name] = get_default_scorecard_row(
            player_name,
            grade,
        )

    for issue in issues:
        player_name = issue["player"]

        if player_name not in rows:
            rows[player_name] = get_default_scorecard_row(player_name)

        row = rows[player_name]

        row["issue_score"] += int(issue.get("score", 0))

        severity = issue.get("severity", "Info")
        severity_column = SEVERITY_COLUMNS.get(severity)

        if severity_column:
            row[severity_column] += 1

        if not row["top_issue"]:
            row["top_issue"] = issue.get("message", "")

    return sorted(
        rows.values(),
        key=lambda row: (
            -row["issue_score"],
            row["grade"],
            row["player"],
        ),
    )