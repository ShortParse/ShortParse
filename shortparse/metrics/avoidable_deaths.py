AVOIDABLE_DAMAGE_BY_ENCOUNTER_ID = {
    # March on Quel'Danas

    3183: {  # Midnight Falls
        1254076,  # Heaven's Glaives
    },

    # The Voidspire

    # 0000: {  # Imperator Averzian
    # },

    # 0000: {  # Vorasius
    # },
}


def get_avoidable_damage_spell_ids(encounter_id: int) -> set[int]:
    return AVOIDABLE_DAMAGE_BY_ENCOUNTER_ID.get(encounter_id, set())


DEATH_LOOKBACK_SECONDS = 8


def calculate_avoidable_deaths(
    actor_id: int,
    events: list[dict],
    death_events: list[dict],
    encounter_id: int,
) -> dict:
    avoidable_spell_ids = get_avoidable_damage_spell_ids(encounter_id)
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

        matched_avoidable = [
            event
            for event in recent_damage_events
            if event.get("abilityGameID") in avoidable_spell_ids
        ]

        if matched_avoidable:
            avoidable_deaths.append(
                {
                    "death_timestamp": death_timestamp,
                    "matched_events": matched_avoidable,
                }
            )

    return {
        "avoidable_death_count": len(avoidable_deaths),
        "avoidable_deaths": avoidable_deaths,
    }