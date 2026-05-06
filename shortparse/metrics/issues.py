ACTIVE_TIME_WARNING_THRESHOLD = 95.0


ISSUE_RULES = {
    "avoidable_death": {
        "severity": "Critical",
        "score": 150,
    },
    "death": {
        "severity": "Critical",
        "score": 100,
    },
    "no_combat_potion": {
        "severity": "Major",
        "score": 40,
    },
    "no_healthstone": {
        "severity": "Warning",
        "score": 20,
    },
    "low_active_time": {
        "severity": "Warning",
        "score": 15,
    },
}


def make_issue(
    rule_key: str,
    player: str,
    category: str,
    message: str,
) -> dict:
    rule = ISSUE_RULES[rule_key]

    return {
        "severity": rule["severity"],
        "score": rule["score"],
        "player": player,
        "category": category,
        "message": message,
    }


def build_player_issues(player_name: str, metric_data: dict) -> list[dict]:
    issues = []

    identity = metric_data["identity"]
    activity = metric_data["activity"]
    performance = metric_data["performance"]
    consumables = metric_data["consumables"]

    role = identity.get("role", "Unknown")

    if performance.get("avoidable_deaths", 0) > 0:
        mechanics = performance.get("avoidable_death_mechanics", [])

        mechanic_names = sorted(
            {
                mechanic.get("name", "Unknown Mechanic")
                for mechanic in mechanics
            }
        )

        mechanic_text = ", ".join(mechanic_names) or "avoidable mechanic"

        issues.append(
            make_issue(
                "avoidable_death",
                player_name,
                "Avoidable Deaths",
                (
                    f"Died to {mechanic_text} "
                    f"{performance['avoidable_deaths']} time(s)."
                ),
            )
        )

    elif performance.get("deaths", 0) > 0:
        issues.append(
            make_issue(
                "death",
                player_name,
                "Deaths",
                f"Died {performance['deaths']} time(s) before wipe window.",
            )
        )

    if consumables.get("combat_potions", 0) == 0:
        issues.append(
            make_issue(
                "no_combat_potion",
                player_name,
                "Consumables",
                "Used 0 combat potions.",
            )
        )

    if consumables.get("healthstone_count", 0) == 0:
        issues.append(
            make_issue(
                "no_healthstone",
                player_name,
                "Consumables",
                "Used 0 healthstones.",
            )
        )

    if activity.get("active_time_pct", 0) < ACTIVE_TIME_WARNING_THRESHOLD:
        issues.append(
            make_issue(
                "low_active_time",
                player_name,
                "Activity",
                (
                    f"{role} active time below {ACTIVE_TIME_WARNING_THRESHOLD:.0f}% "
                    f"({activity['active_time_pct']:.2f}%)."
                ),
            )
        )

    return issues


def build_raid_issues(player_metrics: dict) -> list[dict]:
    issues = []

    for player_name, metric_data in sorted(player_metrics.items()):
        issues.extend(
            build_player_issues(
                player_name,
                metric_data,
            )
        )

    severity_order = {
        "Critical": 0,
        "Major": 1,
        "Warning": 2,
        "Info": 3,
    }

    issues.sort(
        key=lambda issue: (
            severity_order.get(issue["severity"], 99),
            -issue["score"],
            issue["category"],
            issue["player"],
        )
    )

    return issues


def build_player_issue_scores(player_metrics: dict) -> dict[str, int]:
    scores = {}

    for player_name, metric_data in player_metrics.items():
        player_issues = build_player_issues(player_name, metric_data)

        scores[player_name] = sum(
            issue["score"]
            for issue in player_issues
        )

    return scores