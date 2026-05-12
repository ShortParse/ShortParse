from shortparse.data.encounters.constants import ALL_ROLES
from shortparse.metrics.mechanic_rules.models import MechanicFailure


def mechanic_applies_to_player(mechanic: dict, player_role: str) -> bool:
    applies_to = mechanic.get("applies_to", ALL_ROLES)
    return player_role in applies_to


def analyze_avoidable_damage(
    mechanic: dict,
    event: dict,
    player_lookup: dict,
) -> MechanicFailure | None:
    if event.get("type") != "damage":
        return None

    actor_id = event.get("targetID")
    player = player_lookup.get(actor_id)

    if not player:
        return None

    player_name = player["name"]
    player_role = player.get("role", "Unknown")

    if not mechanic_applies_to_player(mechanic, player_role):
        return None

    return MechanicFailure(
        mechanic_name=mechanic["name"],
        player_name=player_name,
        damage=int(event.get("amount") or 0),
    )