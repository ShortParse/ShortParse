from shortparse.metrics.activity import calculate_active_time
from shortparse.metrics.consumables import calculate_consumables
from shortparse.metrics.deaths import calculate_deaths
from shortparse.metrics.avoidable_deaths import calculate_avoidable_deaths
from shortparse.metrics.avoidable_damage import calculate_avoidable_damage
from shortparse.metrics.mechanics import calculate_mechanics
from shortparse.metrics.cooldowns import calculate_cooldowns


def build_player_metrics(
    roster: list[dict],
    events: list[dict],
    fight_duration_seconds: float,
    fight_start_time: int,
    fight_end_time: int,
    encounter_id: int,
) -> dict:

    metrics = {}

    mechanics_data = calculate_mechanics(
        roster,
        events,
        encounter_id,
    )

    player_mechanics = mechanics_data["player_mechanics"]

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

        avoidable_damage = calculate_avoidable_damage(
            player["actor_id"],
            events,
            encounter_id,
        )

        cooldowns = calculate_cooldowns(
            player["actor_id"],
            events,
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
                "dps": round(player["damage_done"] / fight_duration_seconds, 1),
                "hps": round(player["healing_done"] / fight_duration_seconds, 1),
                "dtps": round(player["damage_taken"] / fight_duration_seconds, 1),
                "damage_taken": player["damage_taken"],
                "deaths": deaths["death_count"],
                "death_events": deaths["death_events"],
                "avoidable_deaths": avoidable_deaths["avoidable_death_count"],
                "avoidable_death_mechanics": [
                    mechanic
                    for death in avoidable_deaths["avoidable_deaths"]
                    for mechanic in death.get("matched_mechanics", [])
                ],
                "avoidable_hit_count": avoidable_damage["avoidable_hit_count"],
                "avoidable_damage_taken": avoidable_damage["avoidable_damage_taken"],
                "avoidable_mechanics": avoidable_damage["avoidable_mechanics"],
                "avoidable_damage_events": avoidable_damage["avoidable_damage_events"],
                "mechanics": player_mechanics.get(name, {}),
            },

            "activity": activity,

            "consumables": {
                "combat_potions": potion_count,
                "healthstone_used": healthstone_count > 0,
                "healthstone_count": healthstone_count,
            },

            "cooldowns": cooldowns,

            "utility": {},
        }

    return metrics