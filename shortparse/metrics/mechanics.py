from shortparse.data.encounters.registry import get_avoidable_damage
from shortparse.data.encounters.constants import ALL_ROLES


def mechanic_applies_to_player(
    mechanic: dict,
    player_role: str,
) -> bool:
    applies_to = mechanic.get("applies_to", ALL_ROLES)

    return player_role in applies_to


def get_or_create_raid_entry(
    raid_mechanics: dict,
    mechanic_name: str,
    mechanic: dict,
) -> dict:
    if mechanic_name not in raid_mechanics:
        raid_mechanics[mechanic_name] = {
            "severity": mechanic.get("severity", "Info"),
            "note": mechanic.get("note", ""),
            "recommendation": mechanic.get("recommendation", ""),
            "category": mechanic.get("category", "Unknown"),
            "failure_type": mechanic.get("failure_type", ""),
            "applies_to": mechanic.get("applies_to", ALL_ROLES),
            "hits": 0,
            "damage": 0,
            "players_hit": set(),
            "worst_player": None,
            "worst_hits": 0,
            "player_failures": {},
        }

    return raid_mechanics[mechanic_name]


def add_player_mechanic_failure(
    player_mechanics: dict,
    player_name: str,
    mechanic_name: str,
    damage: int = 0,
) -> None:
    if player_name not in player_mechanics:
        player_mechanics[player_name] = {}

    if mechanic_name not in player_mechanics[player_name]:
        player_mechanics[player_name][mechanic_name] = {
            "hits": 0,
            "damage": 0,
        }

    player_mechanics[player_name][mechanic_name]["hits"] += 1
    player_mechanics[player_name][mechanic_name]["damage"] += damage


def add_raid_mechanic_failure(
    raid_entry: dict,
    player_name: str,
    damage: int = 0,
) -> None:
    raid_entry["hits"] += 1
    raid_entry["damage"] += damage
    raid_entry["players_hit"].add(player_name)

    if player_name not in raid_entry["player_failures"]:
        raid_entry["player_failures"][player_name] = {
            "hits": 0,
            "damage": 0,
        }

    raid_entry["player_failures"][player_name]["hits"] += 1
    raid_entry["player_failures"][player_name]["damage"] += damage


def get_event_source_name(
    event: dict,
) -> str:
    source = event.get("source")

    if isinstance(source, dict):
        name = source.get("name")

        if name:
            return name

    return (
        event.get("sourceName")
        or event.get("source")
        or "Unknown Caster"
    )


def calculate_mechanics(
    roster: list[dict],
    events: list[dict],
    encounter_id: int,
) -> dict:

    mechanics = get_avoidable_damage(encounter_id)

    player_lookup = {
        player["actor_id"]: player
        for player in roster
    }

    player_mechanics = {}
    raid_mechanics = {}

    for event in events:
        spell_id = event.get("abilityGameID")
        mechanic = mechanics.get(spell_id)

        if not mechanic:
            continue

        failure_type = mechanic.get(
            "failure_type",
            "avoidable_damage",
        )

        mechanic_name = mechanic["name"]

        if failure_type == "interrupt":
            if event.get("type") != "cast":
                continue

            caster_name = get_event_source_name(event)

            raid_entry = get_or_create_raid_entry(
                raid_mechanics,
                mechanic_name,
                mechanic,
            )

            add_player_mechanic_failure(
                player_mechanics,
                caster_name,
                mechanic_name,
                damage=0,
            )

            add_raid_mechanic_failure(
                raid_entry,
                caster_name,
                damage=0,
            )

            continue

        if event.get("type") != "damage":
            continue

        actor_id = event.get("targetID")
        player = player_lookup.get(actor_id)

        if not player:
            continue

        player_name = player["name"]
        player_role = player.get("role", "Unknown")

        if not mechanic_applies_to_player(
            mechanic,
            player_role,
        ):
            continue

        damage = int(event.get("amount") or 0)

        add_player_mechanic_failure(
            player_mechanics,
            player_name,
            mechanic_name,
            damage=damage,
        )

        raid_entry = get_or_create_raid_entry(
            raid_mechanics,
            mechanic_name,
            mechanic,
        )

        add_raid_mechanic_failure(
            raid_entry,
            player_name,
            damage=damage,
        )

    for mechanic_name, raid_entry in raid_mechanics.items():
        worst_player = None
        worst_hits = 0

        for player_name, player_data in player_mechanics.items():
            mechanic_data = player_data.get(mechanic_name)

            if not mechanic_data:
                continue

            hits = mechanic_data["hits"]

            if hits > worst_hits:
                worst_hits = hits
                worst_player = player_name

        raid_entry["worst_player"] = worst_player
        raid_entry["worst_hits"] = worst_hits
        raid_entry["players_hit"] = sorted(raid_entry["players_hit"])

    return {
        "player_mechanics": player_mechanics,
        "raid_mechanics": raid_mechanics,
    }