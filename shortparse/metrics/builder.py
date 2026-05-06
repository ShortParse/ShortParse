from shortparse.metrics.activity import calculate_active_time
from shortparse.metrics.consumables import calculate_consumables
from shortparse.metrics.deaths import calculate_deaths
from shortparse.metrics.avoidable_deaths import calculate_avoidable_deaths


def build_player_metrics(
    roster: list[dict],
    events: list[dict],
    fight_duration_seconds: float,
    fight_start_time: int,
    fight_end_time: int,
    encounter_id: int,
) -> dict:

    metrics = {}

    for player in roster:
        name = player["name"]

        activity = calculate_active_time(
            player["actor_id"],
            events,
            fight_duration_seconds,
        )

        consumables = calculate_consumables(
            player["actor_id"],
            events,
        )

        deaths = calculate_deaths(
            player["actor_id"],
            events,
            fight_start_time,
            fight_end_time,
        )

        avoidable_deaths = calculate_avoidable_deaths(
            player["actor_id"],
            events,
            deaths["death_events"],
            encounter_id,
        )

        potion_count = consumables["combat_potions"]
        healthstone_count = consumables["healthstone_count"]

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
                "deaths": deaths["death_count"],
                "death_events": deaths["death_events"],
                "avoidable_deaths": avoidable_deaths["avoidable_death_count"],
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