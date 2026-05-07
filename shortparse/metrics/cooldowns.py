from shortparse.data.cooldowns import get_cooldown, is_raid_cooldown


def calculate_cooldowns(
    actor_id: int,
    events: list[dict],
) -> dict:
    cooldowns_used = {}

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

        if cooldown_name not in cooldowns_used:
            cooldowns_used[cooldown_name] = {
                "spell_id": spell_id,
                "name": cooldown_name,
                "category": cooldown["category"],
                "casts": 0,
                "timestamps": [],
            }

        cooldowns_used[cooldown_name]["casts"] += 1
        cooldowns_used[cooldown_name]["timestamps"].append(
            event.get("timestamp")
        )

    return cooldowns_used