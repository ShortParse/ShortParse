import math

from shortparse.data.cooldowns import (
    get_cooldown,
    get_cooldowns_for_class,
    is_raid_cooldown,
)
from shortparse.data.talents import player_can_access_spell


def calculate_possible_casts(
    fight_duration_seconds: float,
    cooldown_seconds: int,
) -> int:
    if cooldown_seconds <= 0:
        return 0

    return max(
        1,
        math.floor(fight_duration_seconds / cooldown_seconds) + 1,
    )


def build_empty_cooldown_entry(
    spell_id: int,
    cooldown: dict,
    fight_duration_seconds: float,
) -> dict:
    cooldown_seconds = int(
        cooldown.get("cooldown_seconds") or 0
    )

    return {
        "spell_id": spell_id,
        "name": cooldown["name"],
        "category": cooldown["category"],
        "weight": cooldown.get("weight", "medium"),
        "cooldown_seconds": cooldown_seconds,
        "casts": 0,
        "possible_casts": calculate_possible_casts(
            fight_duration_seconds,
            cooldown_seconds,
        ),
        "efficiency_pct": 0.0,
        "timestamps": [],
    }


def preload_expected_cooldowns(
    class_name: str,
    spec_name: str,
    fight_duration_seconds: float,
) -> dict:
    cooldowns_used = {}

    expected_cooldowns = get_cooldowns_for_class(
        class_name,
        spec_name,
    )

    for spell_id, cooldown in expected_cooldowns.items():
        if cooldown.get("optional"):
            continue

        if not player_can_access_spell(
            spell_id,
            class_name,
            spec_name,
        ):
            continue

        cooldowns_used[cooldown["name"]] = build_empty_cooldown_entry(
            spell_id,
            cooldown,
            fight_duration_seconds,
        )

    return cooldowns_used


def calculate_efficiency(
    cooldowns_used: dict,
) -> None:
    for cooldown_data in cooldowns_used.values():
        casts = cooldown_data["casts"]
        possible_casts = cooldown_data["possible_casts"]

        if possible_casts > 0:
            cooldown_data["efficiency_pct"] = round(
                min(casts / possible_casts, 1.0) * 100,
                2,
            )


# Mapping of mutually exclusive cooldown spells: if a player casts key spell ID,
# we exclude the baseline/alternative value spell IDs from their expected audits.
MUTUALLY_EXCLUSIVE_COOLDOWNS = {
    421453: [62618],  # Ultimate Penitence excludes Power Word: Barrier
}


def calculate_cooldowns(
    actor_id: int,
    class_name: str,
    spec_name: str,
    events: list[dict],
    fight_duration_seconds: float,
) -> dict:
    cooldowns_used = preload_expected_cooldowns(
        class_name,
        spec_name,
        fight_duration_seconds,
    )

    for event in events:
        if event.get("sourceID") != actor_id:
            continue

        if event.get("type") != "cast":
            continue

        spell_id = event.get("abilityGameID")

        if not spell_id:
            continue

        # Handle mutual exclusivity checks
        if spell_id in MUTUALLY_EXCLUSIVE_COOLDOWNS:
            for excluded_id in MUTUALLY_EXCLUSIVE_COOLDOWNS[spell_id]:
                excluded_cooldown = get_cooldown(excluded_id)
                if excluded_cooldown:
                    excluded_name = excluded_cooldown["name"]
                    if excluded_name in cooldowns_used:
                        del cooldowns_used[excluded_name]

        if not is_raid_cooldown(spell_id):
            continue

        cooldown = get_cooldown(spell_id)

        if not cooldown:
            continue

        if not player_can_access_spell(
            spell_id,
            class_name,
            spec_name,
        ):
            continue

        cooldown_name = cooldown["name"]

        if cooldown_name not in cooldowns_used:
            cooldowns_used[cooldown_name] = build_empty_cooldown_entry(
                spell_id,
                cooldown,
                fight_duration_seconds,
            )

        cooldowns_used[cooldown_name]["casts"] += 1
        cooldowns_used[cooldown_name]["timestamps"].append(
            event.get("timestamp")
        )

    calculate_efficiency(cooldowns_used)

    return cooldowns_used