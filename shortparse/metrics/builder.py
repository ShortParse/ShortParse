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
    damage_taken_table: dict,
    fight_duration_seconds: float,
    fight_start_time: int,
    fight_end_time: int,
    encounter_id: int,
    fight_data: dict = None,
) -> dict:

    metrics = {}

    master_data = fight_data.get("masterData", {}) if fight_data else {}

    mechanics_data = calculate_mechanics(
        roster,
        events,
        encounter_id,
    )

    player_mechanics = mechanics_data["player_mechanics"]

    # Pre-index events by sourceID and targetID to avoid O(P * E) full list scans inside player loop
    events_by_source = {}
    events_by_target = {}

    for event in events:
        source_id = event.get("sourceID")
        if source_id is not None:
            if source_id not in events_by_source:
                events_by_source[source_id] = []
            events_by_source[source_id].append(event)

        target_id = event.get("targetID")
        if target_id is not None:
            if target_id not in events_by_target:
                events_by_target[target_id] = []
            events_by_target[target_id].append(event)

    for player in roster:
        name = player["name"]
        actor_id = player["actor_id"]

        player_events_source = events_by_source.get(actor_id, [])
        player_events_target = events_by_target.get(actor_id, [])

        activity = calculate_active_time(
            actor_id,
            player_events_source,
            fight_duration_seconds,
            fight_start_time,
        )

        consumables = calculate_consumables(
            actor_id,
            player_events_source,
        )

        deaths = calculate_deaths(
            actor_id,
            player["class"],
            player["spec"],
            player["role"],
            encounter_id,
            player_events_target,
            player_events_source,
            fight_start_time,
            fight_end_time,
            master_data=master_data,
        )

        avoidable_deaths = calculate_avoidable_deaths(
            actor_id,
            player_events_target,
            deaths["death_events"],
            encounter_id,
            player["role"],
        )

        avoidable_damage = calculate_avoidable_damage(
            actor_id,
            player_events_target,
            encounter_id,
            player["role"],
        )

        cooldowns = calculate_cooldowns(
            actor_id,
            player["class"],
            player["spec"],
            player_events_source,
            fight_duration_seconds,
        )

        potion_count = consumables["combat_potions"]
        healthstone_count = consumables["healthstone_count"]

        metrics[name] = {
            "identity": {
                "name": name,
                "actor_id": player["actor_id"],
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