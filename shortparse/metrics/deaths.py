WIPE_DEATH_IGNORE_WINDOW_SECONDS = 15


def calculate_deaths(
    actor_id: int,
    events: list[dict],
    fight_start_time: int,
    fight_end_time: int,
    master_data: dict = None,
) -> dict:
    death_events = []

    ignore_after_timestamp = fight_end_time - (
        WIPE_DEATH_IGNORE_WINDOW_SECONDS * 1000
    )

    # Build lookups from masterData to resolve spell names and actor names
    ability_lookup = {}
    actor_lookup = {}
    if master_data:
        for ability in master_data.get("abilities", []):
            a_id = ability.get("gameID")
            a_name = ability.get("name")
            if a_id is not None and a_name:
                ability_lookup[a_id] = a_name

        for actor in master_data.get("actors", []):
            ac_id = actor.get("id")
            ac_name = actor.get("name")
            if ac_id is not None and ac_name:
                actor_lookup[ac_id] = ac_name

    for event in events:
        if event.get("type") != "death":
            continue

        if event.get("targetID") != actor_id:
            continue

        timestamp = event.get("timestamp")

        if timestamp is None:
            continue

        if timestamp >= ignore_after_timestamp:
            continue

        # Gather lookback events for the visual death recap (final 8 seconds)
        lookback_start = timestamp - 8000
        recap_events = []
        
        from shortparse.data.cooldowns import RAID_COOLDOWNS
        
        for e in events:
            e_type = e.get("type")
            e_timestamp = e.get("timestamp", 0)
            
            if not (lookback_start <= e_timestamp <= timestamp):
                continue
                
            spell_id = e.get("abilityGameID")
            
            # Resolve ability name from masterData lookup first
            ability_name = "Unknown Spell"
            if spell_id in ability_lookup:
                ability_name = ability_lookup[spell_id]
            else:
                ability_dict = e.get("ability")
                if isinstance(ability_dict, dict):
                    ability_name = ability_dict.get("name", "Unknown Spell")
                elif e.get("abilityName"):
                    ability_name = e.get("abilityName")
                
            # Resolve source name from masterData lookup first
            source_id = e.get("sourceID")
            source_name = None
            if source_id in actor_lookup:
                source_name = actor_lookup[source_id]
            else:
                source_name = e.get("sourceName")
                
            # 1. Damage events targeting this player
            if e_type == "damage" and e.get("targetID") == actor_id:
                recap_events.append({
                    "type": "damage",
                    "timestamp": e_timestamp,
                    "seconds_offset": round((e_timestamp - timestamp) / 1000, 2),
                    "amount": int(e.get("amount") or 0),
                    "overkill": int(e.get("overkill") or 0),
                    "ability_id": spell_id,
                    "ability_name": ability_name,
                    "source_name": source_name or "Boss/NPC"
                })
                
            # 2. Heal events targeting this player
            elif e_type == "heal" and e.get("targetID") == actor_id:
                recap_events.append({
                    "type": "heal",
                    "timestamp": e_timestamp,
                    "seconds_offset": round((e_timestamp - timestamp) / 1000, 2),
                    "amount": int(e.get("amount") or 0),
                    "overheal": int(e.get("overheal") or 0),
                    "ability_id": spell_id,
                    "ability_name": ability_name,
                    "source_name": source_name or "Healer"
                })
                
            # 3. Defensive buffs applied/removed on this player
            elif e_type in ("applybuff", "removebuff") and e.get("targetID") == actor_id:
                if spell_id in RAID_COOLDOWNS:
                    cooldown = RAID_COOLDOWNS[spell_id]
                    category = cooldown.get("category", "")
                    if category in ("personal_defensive", "tank_defensive", "external_defensive", "raid_defensive"):
                        recap_events.append({
                            "type": e_type,
                            "timestamp": e_timestamp,
                            "seconds_offset": round((e_timestamp - timestamp) / 1000, 2),
                            "ability_id": spell_id,
                            "ability_name": cooldown.get("name", "Defensive"),
                            "source_name": source_name or "Raid Member"
                        })
                        
        # Sort chronologically by timestamp
        recap_events.sort(key=lambda x: x["timestamp"])

        death_events.append(
            {
                "timestamp": timestamp,
                "seconds_into_fight": round(
                    (timestamp - fight_start_time) / 1000,
                    2,
                ),
                "source_id": event.get("sourceID"),
                "target_id": event.get("targetID"),
                "ability_id": event.get("abilityGameID"),
                "recap": recap_events
            }
        )

    return {
        "death_count": len(death_events),
        "death_events": death_events,
    }