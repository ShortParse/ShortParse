def build_raid_coach_summary(
    fight: dict,
    roster: list[dict],
    player_metrics: dict,
    mechanics: dict,
    benchmarks: dict,
    issues: list[dict],
    scorecard: list[dict],
) -> dict:
    raid_mechanics = mechanics.get("raid_mechanics", {})
    mechanic_rows = []

    for mechanic_name, data in raid_mechanics.items():
        mechanic_rows.append({
            "name": mechanic_name,
            "severity": data.get("severity", "Info"),
            "hits": data.get("hits", 0),
            "damage": data.get("damage", 0),
            "players_hit": len(data.get("players_hit", [])),
            "worst_player": data.get("worst_player"),
            "worst_hits": data.get("worst_hits", 0),
            "note": data.get("note", ""),
            "recommendation": data.get("recommendation", ""),
            "failure_type": data.get("failure_type", ""),
        })

    mechanic_rows.sort(
        key=lambda row: (
            severity_score(row["severity"]),
            row["players_hit"],
            row["hits"],
            row["damage"],
        ),
        reverse=True,
    )

    top_issues = sorted(
        issues,
        key=lambda issue: issue.get("score", 0),
        reverse=True,
    )[:5]

    worst_players = scorecard[:5]

    top_priorities = build_top_priorities(
        mechanic_rows,
        top_issues,
    )

    what_went_well = build_what_went_well(
        fight,
        roster,
        mechanic_rows,
        scorecard,
    )

    needs_attention = build_needs_attention(
        mechanic_rows,
        top_issues,
        worst_players,
    )

    next_pull_focus = build_next_pull_focus(
        mechanic_rows,
        top_issues,
    )

    return {
        "overall_read": build_overall_read(
            fight,
            mechanic_rows,
            issues,
            scorecard,
        ),
        "top_priorities": top_priorities,
        "what_went_well": what_went_well,
        "needs_attention": needs_attention,
        "next_pull_focus": next_pull_focus,
    }


def severity_score(severity: str) -> int:
    scores = {
        "Critical": 4,
        "Major": 3,
        "Warning": 2,
        "Info": 1,
    }

    return scores.get(severity, 0)


def build_overall_read(
    fight: dict,
    mechanic_rows: list[dict],
    issues: list[dict],
    scorecard: list[dict],
) -> str:
    boss_name = fight.get("name", "this encounter")
    result = "kill" if fight.get("kill") else "best progression wipe"

    critical_mechanics = [
        row
        for row in mechanic_rows
        if row["severity"] == "Critical"
    ]

    if fight.get("kill"):
        if critical_mechanics:
            return (
                f"{boss_name} was completed successfully, but the raid still "
                f"had notable mechanical cleanup opportunities. The largest "
                f"concerns were repeated avoidable hits and high issue counts "
                f"on a small number of players."
            )

        return (
            f"{boss_name} was completed successfully with no major tracked "
            f"critical mechanic problems standing out."
        )

    return (
        f"{boss_name} ended as a {result}. The main focus should be reducing "
        f"repeat mechanic failures, stabilizing deaths, and cleaning up the "
        f"highest-scoring player issues before the next pull."
    )


def build_top_priorities(
    mechanic_rows: list[dict],
    top_issues: list[dict],
) -> list[str]:
    priorities = []

    for row in mechanic_rows[:3]:
        rec = row.get("recommendation") or row.get("note") or ""
        rec_suffix = f" Tips: {rec}" if rec else ""
        priorities.append(
            (
                f"Clean up {row['name']} — {row['hits']} hits across "
                f"{row['players_hit']} player(s), with {row['worst_player'] or 'unknown'} "
                f"having the most hits.{rec_suffix}"
            )
        )

    for issue in top_issues[:2]:
        player = issue.get("player", "Unknown player")
        message = issue.get("message", "High priority issue detected.")
        priorities.append(f"Review {player}: {message}")

    return priorities[:5]


def build_what_went_well(
    fight: dict,
    roster: list[dict],
    mechanic_rows: list[dict],
    scorecard: list[dict],
) -> list[str]:
    items = []

    if fight.get("kill"):
        items.append("The encounter ended in a kill.")

    items.append(f"{len(roster)} players were evaluated successfully.")

    if mechanic_rows:
        items.append(f"{len(mechanic_rows)} tracked mechanics were summarized cleanly.")

    good_grades = [
        row
        for row in scorecard
        if row.get("grade") in ("S", "A", "B")
    ]

    if good_grades:
        items.append(f"{len(good_grades)} players graded B or higher.")

    return items


def build_needs_attention(
    mechanic_rows: list[dict],
    top_issues: list[dict],
    worst_players: list[dict],
) -> list[str]:
    items = []

    critical_rows = [
        row
        for row in mechanic_rows
        if row["severity"] == "Critical"
    ]

    if critical_rows:
        items.append(f"{len(critical_rows)} critical tracked mechanic(s) caused failures.")

    if top_issues:
        items.append(f"{len(top_issues)} high-priority issue(s) should be reviewed.")

    for player in worst_players[:3]:
        items.append(
            (
                f"{player.get('player', 'Unknown player')} had an issue score of "
                f"{player.get('issue_score', 'N/A')}."
            )
        )

    return items


def build_next_pull_focus(
    mechanic_rows: list[dict],
    top_issues: list[dict],
) -> list[str]:
    focus = []

    for row in mechanic_rows[:2]:
        rec = row.get("recommendation") or row.get("note") or ""
        rec_suffix = f" ({rec})" if rec else ""
        focus.append(
            (
                f"Reduce {row['name']} failures, especially from "
                f"{row['worst_player'] or 'repeat offenders'}.{rec_suffix}"
            )
        )

    if top_issues:
        focus.append("Review the top issue list before the next pull.")

    focus.append("Use the Mechanics tab to drill into player-specific failures.")

    return focus[:4]