from shortparse.data.encounters.registry import get_avoidable_damage
from shortparse.data.encounters.constants import ALL_ROLES


DEATH_LOOKBACK_SECONDS = 8


def mechanic_applies_to_player(
    mechanic: dict,
    player_role: str,
) -> bool:
    applies_to = mechanic.get("applies_to", ALL_ROLES)

    return player_role in applies_to


def calculate_avoidable_deaths(
    actor_id: int,
    events: list[dict],
    death_events: list[dict],
    encounter_id: int,
    player_role: str = "Unknown",
) -> dict:
    avoidable_mechanics = get_avoidable_damage(encounter_id)

    if not avoidable_mechanics:
        return {
            "avoidable_death_count": 0,
            "avoidable_deaths": [],
        }

    avoidable_deaths = []

    for death in death_events:
        death_timestamp = death.get("timestamp")

        if death_timestamp is None:
            continue

        lookback_start = (
            death_timestamp
            - (DEATH_LOOKBACK_SECONDS * 1000)
        )

        matched_mechanics = []

        for event in events:
            if event.get("type") != "damage":
                continue

            if event.get("targetID") != actor_id:
                continue

            timestamp = event.get("timestamp", 0)

            if timestamp < lookback_start:
                continue

            if timestamp > death_timestamp:
                continue

            spell_id = event.get("abilityGameID")
            mechanic = avoidable_mechanics.get(spell_id)

            if not mechanic:
                continue

            if not mechanic_applies_to_player(
                mechanic,
                player_role,
            ):
                continue

            matched_mechanics.append(
                {
                    "spell_id": spell_id,
                    "name": mechanic["name"],
                    "severity": mechanic.get("severity", "Critical"),
                    "timestamp": timestamp,
                    "amount": int(event.get("amount") or 0),
                }
            )

        if not matched_mechanics:
            continue

        unique_mechanics = {}

        for mechanic in matched_mechanics:
            key = (
                mechanic["spell_id"],
                mechanic["timestamp"],
            )

            existing = unique_mechanics.get(key)

            if (
                not existing
                or mechanic["amount"] > existing["amount"]
            ):
                unique_mechanics[key] = mechanic

        avoidable_deaths.append(
            {
                "death_timestamp": death_timestamp,
                "matched_mechanics": list(unique_mechanics.values()),
            }
        )

    return {
        "avoidable_death_count": len(avoidable_deaths),
        "avoidable_deaths": avoidable_deaths,
    }