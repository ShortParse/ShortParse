from shortparse.data.encounters.constants import ALL_ROLES
from shortparse.metrics.mechanic_rules.models import MechanicFailure


def mechanic_applies_to_player(
    mechanic: dict,
    player_role: str,
) -> bool:
    applies_to = mechanic.get("applies_to", ALL_ROLES)

    return player_role in applies_to


def analyze_required_soak(
    mechanic: dict,
    events: list[dict],
    roster: list[dict],
    player_lookup: dict,
) -> list[MechanicFailure]:
    spell_ids = set(mechanic.get("spell_ids", []))

    if not spell_ids:
        return []

    soaked_player_ids = set()

    for event in events:
        if event.get("type") != "damage":
            continue

        if event.get("abilityGameID") not in spell_ids:
            continue

        target_id = event.get("targetID")

        if target_id is not None:
            soaked_player_ids.add(target_id)

    failures = []

    for player in roster:
        player_role = player.get("role", "Unknown")

        if not mechanic_applies_to_player(
            mechanic,
            player_role,
        ):
            continue

        actor_id = player.get("actor_id")

        if actor_id in soaked_player_ids:
            continue

        failures.append(
            MechanicFailure(
                mechanic_name=mechanic["name"],
                player_name=player["name"],
                damage=0,
            )
        )

    return failures