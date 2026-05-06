from shortparse.metrics.activity import calculate_active_time


def build_player_metrics(
    roster: list[dict],
    events: list[dict],
    fight_duration_seconds: float,
) -> dict:

    metrics = {}

    for player in roster:
        name = player["name"]

        activity = calculate_active_time(
            player["actor_id"],
            events,
            fight_duration_seconds,
        )

        potion_count = int(player.get("potion_use") or 0)
        healthstone_count = int(player.get("healthstone_use") or 0)

        metrics[name] = {
            "identity": {
                "name": name,
                "class": player["class"],
                "spec": player["spec"],
                "role": player["role"],
                "item_level": player["item_level"],
            },

            "performance": {
                "damage_done": player["damage_done"],
                "healing_done": player["healing_done"],
                "damage_taken": player["damage_taken"],
                "deaths": player["deaths"],
            },

            "activity": activity,

            "consumables": {
                "combat_potions": potion_count,
                "healthstone_used": healthstone_count > 0,
                "healthstone_count": healthstone_count,
            },

            "cooldowns": {},

            "utility": {},
        }

    return metrics