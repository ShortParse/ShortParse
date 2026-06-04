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


def build_mechanic_summary(
    target_name: str | None,
    mechanic_name: str,
    hits: int,
    amount: int,
) -> str:
    player_name = target_name or "Unknown"

    if hits == 1:
        return (
            f"{player_name} was hit by "
            f"{mechanic_name} for {amount:,}."
        )

    return (
        f"{player_name} was hit by {mechanic_name} "
        f"{hits} time(s) for {amount:,} total."
    )


def aggregate_mechanic_events(
    timeline: list[dict],
) -> list[dict]:
    aggregated = []
    mechanic_groups = {}

    for entry in timeline:
        if entry.get("type") != "mechanic":
            aggregated.append(entry)
            continue

        group_key = (
            entry.get("time"),
            entry.get("target"),
            entry.get("spell_id"),
        )

        if group_key not in mechanic_groups:
            mechanic_groups[group_key] = {
                **entry,
                "hits": 0,
                "amount": 0,
            }

        mechanic_groups[group_key]["hits"] += 1
        mechanic_groups[group_key]["amount"] += int(
            entry.get("amount") or 0
        )

    for entry in mechanic_groups.values():
        entry["summary"] = build_mechanic_summary(
            entry.get("target"),
            entry.get("spell_name", "Unknown"),
            entry["hits"],
            entry["amount"],
        )

        aggregated.append(entry)

    aggregated.sort(
        key=lambda entry: entry["timestamp"]
    )

    return aggregated


def build_timeline(
    roster: list[dict],
    events: list[dict],
    fight_start_time: int,
    fight_end_time: int,
    encounter_id: int,
) -> list[dict]:
    wipe_window_ms = 15 * 1000

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
        spell_id = event.get("abilityGameID")

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
                source_name = get_actor_name(source_id, actor_lookup)
                target_name = get_actor_name(target_id, actor_lookup)

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

            #
            # Ignore wipe/reset deaths near encounter end
            #

            if timestamp >= (
                    fight_end_time - wipe_window_ms
            ):
                continue
                
            source_name = get_actor_name(source_id, actor_lookup)
            target_name = get_actor_name(target_id, actor_lookup)
            dead_player = target_name or source_name

            if not dead_player:
                continue

            spell_name = get_ability_name(event)

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
                    "summary": f"{dead_player} died.",
                }
            )

            continue

        #
        # Tracked avoidable mechanics
        #

        if event_type == "damage" and spell_id in avoidable_mechanics:
            # For Belo'ren (Death Drop): Everyone takes damage, but if it is under 100k, they stood far enough away.
            if spell_id == 1241333 and int(event.get("amount") or 0) < 100000:
                continue

            mechanic = avoidable_mechanics[spell_id]
            if not mechanic.get("avoidable", True) or not mechanic.get("counts_as_failure", True):
                continue

            mechanic_name = mechanic["name"]
            source_name = get_actor_name(source_id, actor_lookup)
            target_name = get_actor_name(target_id, actor_lookup)

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

    return aggregate_mechanic_events(timeline)