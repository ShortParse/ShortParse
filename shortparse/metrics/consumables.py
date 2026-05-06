CONSUMABLE_KEYWORDS = {
    "healthstone": [
        "healthstone",
    ],

    "combat_potion": [
        "potion",
    ],
}


def contains_any(text: str, keywords: list[str]) -> bool:
    text = (text or "").lower()

    return any(keyword in text for keyword in keywords)


def calculate_consumables(
    actor_id: int,
    events: list[dict],
) -> dict:

    healthstone_used = False
    combat_potions = 0

    for event in events:
        if event.get("sourceID") != actor_id:
            continue

        event_type = event.get("type", "")

        if event_type not in {
            "cast",
            "applybuff",
        }:
            continue

        ability_name = (
            event.get("ability")
            or event.get("abilityName")
            or ""
        )

        if isinstance(ability_name, dict):
            ability_name = ability_name.get("name", "")

        ability_name = str(ability_name).lower()

        if contains_any(
            ability_name,
            CONSUMABLE_KEYWORDS["healthstone"],
        ):
            healthstone_used = True

        if contains_any(
            ability_name,
            CONSUMABLE_KEYWORDS["combat_potion"],
        ):
            combat_potions += 1

    return {
        "healthstone_used": healthstone_used,
        "combat_potions": combat_potions,
    }