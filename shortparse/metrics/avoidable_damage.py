from shortparse.data.encounters.registry import get_avoidable_damage


def calculate_avoidable_damage(
    actor_id: int,
    events: list[dict],
    encounter_id: int,
) -> dict:
    avoidable_mechanics = get_avoidable_damage(encounter_id)

    if not avoidable_mechanics:
        return {
            "avoidable_hit_count": 0,
            "avoidable_damage_taken": 0,
            "avoidable_damage_events": [],
            "avoidable_mechanics": [],
        }

    avoidable_events = []

    for event in events:
        if event.get("type") != "damage":
            continue

        if event.get("targetID") != actor_id:
            continue

        spell_id = event.get("abilityGameID")
        mechanic = avoidable_mechanics.get(spell_id)

        if not mechanic:
            continue

        avoidable_events.append(
            {
                "spell_id": spell_id,
                "name": mechanic["name"],
                "severity": mechanic.get("severity", "Critical"),
                "timestamp": event.get("timestamp"),
                "amount": int(event.get("amount") or 0),
            }
        )

    mechanic_names = sorted(
        {
            event["name"]
            for event in avoidable_events
        }
    )

    return {
        "avoidable_hit_count": len(avoidable_events),
        "avoidable_damage_taken": sum(
            event["amount"]
            for event in avoidable_events
        ),
        "avoidable_damage_events": avoidable_events,
        "avoidable_mechanics": mechanic_names,
    }