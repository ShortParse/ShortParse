import math

from shortparse.data.cooldowns import (
    get_cooldown,
    get_cooldowns_for_class,
    is_raid_cooldown,
)


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


def calculate_cooldowns(
    actor_id: int,
    class_name: str,
    spec_name: str,
    events: list[dict],
    fight_duration_seconds: float,
) -> dict:
    cooldowns_used = {}

    expected_cooldowns = get_cooldowns_for_class(
        class_name,
        spec_name,
    )

    for spell_id, cooldown in expected_cooldowns.items():
        cooldown_seconds = int(cooldown.get("cooldown_seconds") or 0)

        cooldowns_used[cooldown["name"]] = {
            "spell_id": spell_id,
            "name": cooldown["name"],
            "category": cooldown["category"],
            "cooldown_seconds": cooldown_seconds,
            "casts": 0,
            "possible_casts": calculate_possible_casts(
                fight_duration_seconds,
                cooldown_seconds,
            ),
            "efficiency_pct": 0.0,
            "timestamps": [],
        }

    for event in events:
        if event.get("sourceID") != actor_id:
            continue

        if event.get("type") != "cast":
            continue

        spell_id = event.get("abilityGameID")

        if not spell_id:
            continue

        if not is_raid_cooldown(spell_id):
            continue

        cooldown = get_cooldown(spell_id)

        if not cooldown:
            continue

        cooldown_name = cooldown["name"]
        cooldown_seconds = int(cooldown.get("cooldown_seconds") or 0)

        if cooldown_name not in cooldowns_used:
            cooldowns_used[cooldown_name] = {
                "spell_id": spell_id,
                "name": cooldown_name,
                "category": cooldown["category"],
                "cooldown_seconds": cooldown_seconds,
                "casts": 0,
                "possible_casts": calculate_possible_casts(
                    fight_duration_seconds,
                    cooldown_seconds,
                ),
                "efficiency_pct": 0.0,
                "timestamps": [],
            }

        cooldowns_used[cooldown_name]["casts"] += 1
        cooldowns_used[cooldown_name]["timestamps"].append(
            event.get("timestamp")
        )

    for cooldown_data in cooldowns_used.values():
        casts = cooldown_data["casts"]
        possible_casts = cooldown_data["possible_casts"]

        if possible_casts > 0:
            cooldown_data["efficiency_pct"] = round(
                min(casts / possible_casts, 1.0) * 100,
                2,
            )

    return cooldowns_used