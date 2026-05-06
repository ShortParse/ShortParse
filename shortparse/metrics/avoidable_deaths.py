AVOIDABLE_DAMAGE_BY_ENCOUNTER_ID = {
    ## THE VOIDSPIRE

    ## THE DREAMRIFT

    ## MARCH ON QUEL'DANAS
    3183: {  # Midnight Falls
        1254076: {
            "name": "Heaven's Glaives",
            "severity": "Critical",
        },
    },
}


def get_avoidable_mechanics(encounter_id: int) -> dict:
    return AVOIDABLE_DAMAGE_BY_ENCOUNTER_ID.get(encounter_id, {})


def get_avoidable_mechanic(encounter_id: int, spell_id: int) -> dict | None:
    return get_avoidable_mechanics(encounter_id).get(spell_id)


DEATH_LOOKBACK_SECONDS = 8


def calculate_avoidable_deaths(
    actor_id: int,
    events: list[dict],
    death_events: list[dict],
    encounter_id: int,
) -> dict:
    avoidable_deaths = []

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
            mechanic = get_avoidable_mechanic(encounter_id, spell_id)

            if mechanic:
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