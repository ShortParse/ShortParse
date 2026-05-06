WIPE_DEATH_IGNORE_WINDOW_SECONDS = 15


def calculate_deaths(
    actor_id: int,
    events: list[dict],
    fight_start_time: int,
    fight_end_time: int,
) -> dict:
    death_events = []

    ignore_after_timestamp = fight_end_time - (
        WIPE_DEATH_IGNORE_WINDOW_SECONDS * 1000
    )

    for event in events:
        if event.get("type") != "death":
            continue

        if event.get("targetID") != actor_id:
            continue

        timestamp = event.get("timestamp")

        if timestamp is None:
            continue

        if timestamp >= ignore_after_timestamp:
            continue

        death_events.append(
            {
                "timestamp": timestamp,
                "seconds_into_fight": round(
                    (timestamp - fight_start_time) / 1000,
                    2,
                ),
                "source_id": event.get("sourceID"),
                "target_id": event.get("targetID"),
                "ability_id": event.get("abilityGameID"),
            }
        )

    return {
        "death_count": len(death_events),
        "death_events": death_events,
    }