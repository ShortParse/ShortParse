HEALTHSTONE_SPELL_IDS = {
    6262,
}

COMBAT_POTION_SPELL_IDS = {
    1236616,  # Light's Potential
}


def calculate_consumables(
    actor_id: int,
    events: list[dict],
) -> dict:

    healthstone_count = 0
    combat_potions = 0

    for event in events:
        if event.get("sourceID") != actor_id:
            continue

        if event.get("type") != "cast":
            continue

        if event.get("fake"):
            continue

        spell_id = event.get("abilityGameID")

        if spell_id in HEALTHSTONE_SPELL_IDS:
            healthstone_count += 1

        if spell_id in COMBAT_POTION_SPELL_IDS:
            combat_potions += 1

    return {
        "healthstone_used": healthstone_count > 0,
        "healthstone_count": healthstone_count,
        "combat_potions": combat_potions,
    }