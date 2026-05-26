from shortparse.data.encounters.registry import get_avoidable_damage
from shortparse.data.encounters.constants import ALL_ROLES


def mechanic_applies_to_player(
    mechanic: dict,
    player_role: str,
) -> bool:
    applies_to = mechanic.get("applies_to", ALL_ROLES)

    return player_role in applies_to


def calculate_avoidable_damage(
    actor_id: int,
    events: list[dict],
    encounter_id: int,
    player_role: str = "Unknown",
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

        # For Belo'ren (Death Drop): Everyone takes damage, but if it is under 100k, they stood far enough away.
        if spell_id == 1241333 and int(event.get("amount") or 0) < 100000:
            continue

        if not mechanic_applies_to_player(
            mechanic,
            player_role,
        ):
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