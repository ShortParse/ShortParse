ACTIVE_TIME_WARNING_THRESHOLD = 95.0


def build_player_issues(player_name: str, metric_data: dict) -> list[dict]:
    issues = []

    identity = metric_data["identity"]
    activity = metric_data["activity"]
    performance = metric_data["performance"]
    consumables = metric_data["consumables"]

    role = identity.get("role", "Unknown")

    if performance.get("deaths", 0) > 0:
        issues.append(
            {
                "severity": "Info",
                "player": player_name,
                "category": "Deaths",
                "message": f"Died {performance['deaths']} time(s).",
            }
        )

    if consumables.get("combat_potions", 0) == 0:
        issues.append(
            {
                "severity": "Warning",
                "player": player_name,
                "category": "Consumables",
                "message": "Used 0 combat potions.",
            }
        )

    if consumables.get("healthstone_count", 0) == 0:
        issues.append(
            {
                "severity": "Warning",
                "player": player_name,
                "category": "Consumables",
                "message": "Used 0 healthstones.",
            }
        )

    if activity.get("active_time_pct", 0) < ACTIVE_TIME_WARNING_THRESHOLD:
        issues.append(
            {
                "severity": "Warning",
                "player": player_name,
                "category": "Activity",
                "message": (
                    f"{role} active time below {ACTIVE_TIME_WARNING_THRESHOLD:.0f}% "
                    f"({activity['active_time_pct']:.2f}%)."
                ),
            }
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
        "Warning": 1,
        "Info": 2,
    }

    issues.sort(
        key=lambda issue: (
            severity_order.get(issue["severity"], 99),
            issue["category"],
            issue["player"],
        )
    )

    return issues