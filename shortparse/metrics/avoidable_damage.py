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
        spell_id = event.get("abilityGameID")

        # =========================================================
        # DEBUG: Midnight Falls avoidable damage investigation
        # =========================================================
        if (
            encounter_id == 3183
            and spell_id in avoidable_mechanics
        ):
            print(
                "DEBUG FOUND SPELL:",
                {
                    "spell_id": spell_id,
                    "spell_name": avoidable_mechanics[spell_id]["name"],
                    "event_type": event.get("type"),
                    "targetID": event.get("targetID"),
                    "sourceID": event.get("sourceID"),
                    "amount": event.get("amount"),
                    "timestamp": event.get("timestamp"),
                },
            )

        # =========================================================
        # Only count damage events against this actor
        # =========================================================
        if event.get("targetID") != actor_id:
            continue

        if event.get("type") != "damage":
            continue

        mechanic = avoidable_mechanics.get(spell_id)

        if not mechanic:
            continue

        print(
            "DEBUG MATCHED AVOIDABLE DAMAGE:",
            {
                "actor_id": actor_id,
                "spell_id": spell_id,
                "spell_name": mechanic["name"],
                "amount": event.get("amount"),
                "timestamp": event.get("timestamp"),
            },
        )

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