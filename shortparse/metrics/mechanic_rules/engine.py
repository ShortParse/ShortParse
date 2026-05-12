from shortparse.data.encounters.registry import get_avoidable_damage
from shortparse.data.encounters.constants import ALL_ROLES

from shortparse.metrics.mechanic_rules.handlers.avoidable_damage import (
    analyze_avoidable_damage,
)
from shortparse.metrics.mechanic_rules.handlers.missed_interrupt import (
    analyze_missed_interrupt,
)

from shortparse.metrics.mechanic_rules.handlers.required_soak import (
    analyze_required_soak,
)

HANDLERS = {
    "avoidable_damage": analyze_avoidable_damage,
    "interrupt": analyze_missed_interrupt,
    "missed_interrupt": analyze_missed_interrupt,
    "required_soak": analyze_required_soak,

    # These are intentionally stubbed for now.
    # They require full-fight/window-level analysis later.
    "bad_soak": None,
}


DAMAGE_LIKE_FAILURE_TYPES = {
    "dodge_adds",
    "dodge_oneshot",
    "spread_out",
    "ground_effect",
    "boss_threat",
    "dodge_gravity",
}

WHOLE_FIGHT_FAILURE_TYPES = {
    "required_soak",
}


def normalize_failure_type(failure_type: str) -> str:
    if failure_type in DAMAGE_LIKE_FAILURE_TYPES:
        return "avoidable_damage"

    return failure_type or "avoidable_damage"


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


def finalize_raid_mechanics(
    raid_mechanics: dict,
    player_mechanics: dict,
) -> None:
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

    processed_whole_fight_mechanics = set()

    for spell_id, mechanic in mechanics.items():
        failure_type = normalize_failure_type(
            mechanic.get("failure_type", "avoidable_damage")
        )

        if failure_type not in WHOLE_FIGHT_FAILURE_TYPES:
            continue

        mechanic_name = mechanic["name"]

        if mechanic_name in processed_whole_fight_mechanics:
            continue

        processed_whole_fight_mechanics.add(mechanic_name)

        handler = HANDLERS.get(failure_type)

        if not handler:
            continue

        failures = handler(
            mechanic=mechanic,
            events=events,
            roster=roster,
            player_lookup=player_lookup,
        )

        for failure in failures:
            raid_entry = get_or_create_raid_entry(
                raid_mechanics,
                failure.mechanic_name,
                mechanic,
            )

            add_player_mechanic_failure(
                player_mechanics,
                failure.player_name,
                failure.mechanic_name,
                damage=failure.damage,
            )

            add_raid_mechanic_failure(
                raid_entry,
                failure.player_name,
                damage=failure.damage,
            )

    for event in events:
        spell_id = event.get("abilityGameID")
        mechanic = mechanics.get(spell_id)

        if not mechanic:
            continue

        mechanic_name = mechanic["name"]

        failure_type = normalize_failure_type(
            mechanic.get("failure_type", "avoidable_damage")
        )

        if failure_type in WHOLE_FIGHT_FAILURE_TYPES:
            continue

        handler = HANDLERS.get(failure_type)

        if not handler:
            continue

        failure = handler(
            mechanic=mechanic,
            event=event,
            player_lookup=player_lookup,
        )

        if not failure:
            continue

        raid_entry = get_or_create_raid_entry(
            raid_mechanics,
            mechanic_name,
            mechanic,
        )

        add_player_mechanic_failure(
            player_mechanics,
            failure.player_name,
            failure.mechanic_name,
            damage=failure.damage,
        )

        add_raid_mechanic_failure(
            raid_entry,
            failure.player_name,
            damage=failure.damage,
        )

    finalize_raid_mechanics(
        raid_mechanics,
        player_mechanics,
    )

    return {
        "player_mechanics": player_mechanics,
        "raid_mechanics": raid_mechanics,
    }