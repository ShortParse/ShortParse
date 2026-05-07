from shortparse.data.cooldowns import get_cooldown, is_raid_cooldown
from shortparse.data.encounters.registry import get_avoidable_damage


def format_fight_time(
    timestamp: int,
    fight_start_time: int,
) -> str:
    elapsed_ms = max(0, int(timestamp - fight_start_time))
    elapsed_seconds = elapsed_ms // 1000

    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60

    return f"{minutes:02d}:{seconds:02d}"


def get_actor_name(
    actor_id: int | None,
    actor_lookup: dict[int, str],
) -> str | None:
    if actor_id is None:
        return None

    return actor_lookup.get(actor_id)


def get_ability_name(event: dict) -> str:
    ability = event.get("ability")

    if isinstance(ability, dict):
        return ability.get("name", "Unknown")

    if isinstance(ability, str):
        return ability

    return (
        event.get("abilityName")
        or event.get("name")
        or "Unknown"
    )


def build_actor_lookup(roster: list[dict]) -> dict[int, str]:
    return {
        player["actor_id"]: player["name"]
        for player in roster
        if player.get("actor_id") is not None
    }


def build_timeline(
    roster: list[dict],
    events: list[dict],
    fight_start_time: int,
    encounter_id: int,
) -> list[dict]:

    actor_lookup = build_actor_lookup(roster)
    avoidable_mechanics = get_avoidable_damage(encounter_id)

    timeline = []

    for event in events:
        timestamp = event.get("timestamp")

        if timestamp is None:
            continue

        event_type = event.get("type")

        source_id = event.get("sourceID")
        target_id = event.get("targetID")

        source_name = get_actor_name(
            source_id,
            actor_lookup,
        )

        target_name = get_actor_name(
            target_id,
            actor_lookup,
        )

        spell_id = event.get("abilityGameID")
        spell_name = get_ability_name(event)

        #
        # Tracked cooldown casts
        #

        if (
            event_type == "cast"
            and spell_id
            and is_raid_cooldown(spell_id)
        ):
            cooldown = get_cooldown(spell_id)

            if cooldown:
                cooldown_name = cooldown["name"]

                timeline.append(
                    {
                        "timestamp": timestamp,
                        "time": format_fight_time(
                            timestamp,
                            fight_start_time,
                        ),
                        "type": "cooldown",
                        "source": source_name,
                        "target": target_name,
                        "spell_id": spell_id,
                        "spell_name": cooldown_name,
                        "summary": (
                            f"{source_name or 'Unknown'} cast "
                            f"{cooldown_name}."
                        ),
                    }
                )

            continue

        #
        # Deaths
        #

        if event_type == "death":
            timeline.append(
                {
                    "timestamp": timestamp,
                    "time": format_fight_time(
                        timestamp,
                        fight_start_time,
                    ),
                    "type": "death",
                    "source": source_name,
                    "target": target_name,
                    "spell_id": spell_id,
                    "spell_name": spell_name,
                    "summary": (
                        f"{target_name or source_name or 'Unknown'} died."
                    ),
                }
            )

            continue

        #
        # Tracked avoidable mechanics
        #

        if event_type == "damage" and spell_id in avoidable_mechanics:
            mechanic = avoidable_mechanics[spell_id]
            mechanic_name = mechanic["name"]

            amount = int(event.get("amount") or 0)

            timeline.append(
                {
                    "timestamp": timestamp,
                    "time": format_fight_time(
                        timestamp,
                        fight_start_time,
                    ),
                    "type": "mechanic",
                    "source": source_name,
                    "target": target_name,
                    "spell_id": spell_id,
                    "spell_name": mechanic_name,
                    "amount": amount,
                    "summary": (
                        f"{target_name or 'Unknown'} was hit by "
                        f"{mechanic_name} for {amount:,}."
                    ),
                }
            )

    timeline.sort(
        key=lambda entry: entry["timestamp"]
    )

    return timeline