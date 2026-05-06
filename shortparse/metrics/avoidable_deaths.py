from shortparse.data.encounters.registry import get_avoidable_damage


DEATH_LOOKBACK_SECONDS = 8


def calculate_avoidable_deaths(
    actor_id: int,
    events: list[dict],
    death_events: list[dict],
    encounter_id: int,
) -> dict:
    avoidable_mechanics = get_avoidable_damage(encounter_id)
    avoidable_deaths = []

    if not avoidable_mechanics:
        return {
            "avoidable_death_count": 0,
            "avoidable_deaths": [],
        }

    for death in death_events:
        death_timestamp = death.get("timestamp")

        if death_timestamp is None:
            continue

        lookback_start = death_timestamp - (DEATH_LOOKBACK_SECONDS * 1000)

        recent_damage_events = [
            event
            for event in events
            if event.get("targetID") == actor_id
            and event.get("type") == "damage"
            and lookback_start <= event.get("timestamp", 0) <= death_timestamp
        ]

        matched_mechanics = []

        for event in recent_damage_events:
            spell_id = event.get("abilityGameID")
            mechanic = avoidable_mechanics.get(spell_id)

            if not mechanic:
                continue

            matched_mechanics.append(
                {
                    "spell_id": spell_id,
                    "name": mechanic["name"],
                    "severity": mechanic.get("severity", "Critical"),
                    "timestamp": event.get("timestamp"),
                    "amount": event.get("amount", 0),
                }
            )

        if matched_mechanics:
            avoidable_deaths.append(
                {
                    "death_timestamp": death_timestamp,
                    "matched_mechanics": matched_mechanics,
                }
            )

    return {
        "avoidable_death_count": len(avoidable_deaths),
        "avoidable_deaths": avoidable_deaths,
    }