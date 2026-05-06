def calculate_deaths(
    actor_id: int,
    events: list[dict],
) -> dict:
    death_events = []

    for event in events:
        if event.get("type") != "death":
            continue

        if event.get("targetID") != actor_id:
            continue

        timestamp = event.get("timestamp")

        death_events.append(
            {
                "timestamp": timestamp,
                "source_id": event.get("sourceID"),
                "target_id": event.get("targetID"),
                "ability_id": event.get("abilityGameID"),
            }
        )

    return {
        "death_count": len(death_events),
        "death_events": death_events,
    }