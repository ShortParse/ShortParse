# shortparse/metrics/deaths.py

from shortparse.data.cooldowns import get_cooldowns_for_class, RAID_COOLDOWNS
from shortparse.data.encounters.registry import get_avoidable_damage
from shortparse.metrics.avoidable_deaths import mechanic_applies_to_player
from shortparse.metrics.consumables import HEALTHSTONE_SPELL_IDS, COMBAT_POTION_SPELL_IDS

WIPE_DEATH_IGNORE_WINDOW_SECONDS = 15


def calculate_deaths(
    actor_id: int,
    class_name: str,
    spec_name: str,
    player_role: str,
    encounter_id: int,
    player_events_target: list[dict],
    player_events_source: list[dict],
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

    # Gather candidate personal defensives for this class/spec
    class_cooldowns = get_cooldowns_for_class(class_name, spec_name)
    personal_defensives = []
    for spell_id, cd in class_cooldowns.items():
        cat = cd.get("category", "")
        weight = cd.get("weight", "medium")
        if weight == "low":
            continue
        if cat in ("personal_defensive", "personal_immunity", "tank_defensive"):
            personal_defensives.append({
                "spell_id": spell_id,
                "name": cd.get("name"),
                "cooldown_seconds": cd.get("cooldown_seconds", 0)
            })

    # Track all casts of personal defensives, Healthstone, and Potions by this player
    defensive_casts = {pd["spell_id"]: [] for pd in personal_defensives}
    healthstone_casts = []
    potion_casts = []

    for event in player_events_source:
        if event.get("type") != "cast":
            continue
        spell_id = event.get("abilityGameID")
        if not spell_id:
            continue
        
        timestamp = event.get("timestamp")
        if spell_id in defensive_casts:
            defensive_casts[spell_id].append(timestamp)
        elif spell_id in HEALTHSTONE_SPELL_IDS:
            healthstone_casts.append(timestamp)
        elif spell_id in COMBAT_POTION_SPELL_IDS:
            potion_casts.append(timestamp)

    # Avoidable damage registry for the current encounter
    avoidable_mechanics = get_avoidable_damage(encounter_id) or {}

    for event in player_events_target:
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
        
        total_avoidable_dmg = 0
        avoidable_damage_hits = []
        avoidable_names = set()
        
        for e in player_events_target:
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

            is_avoidable = False
            if spell_id in avoidable_mechanics:
                mech = avoidable_mechanics[spell_id]
                if mech.get("avoidable", True) and mech.get("counts_as_failure", True):
                    if mechanic_applies_to_player(mech, player_role):
                        is_avoidable = True
                
            # 1. Damage events targeting this player
            if e_type == "damage" and e.get("targetID") == actor_id:
                amount = int(e.get("amount") or 0)
                event_data = {
                    "type": "damage",
                    "timestamp": e_timestamp,
                    "seconds_offset": round((e_timestamp - timestamp) / 1000, 2),
                    "amount": amount,
                    "overkill": int(e.get("overkill") or 0),
                    "ability_id": spell_id,
                    "ability_name": ability_name,
                    "source_name": source_name or "Boss/NPC"
                }
                if is_avoidable:
                    event_data["avoidable"] = True
                    total_avoidable_dmg += amount
                    avoidable_names.add(ability_name)
                    avoidable_damage_hits.append({
                        "name": ability_name,
                        "amount": amount,
                        "timestamp": e_timestamp
                    })
                recap_events.append(event_data)
                
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

        # Calculate healing gaps in the final 4 seconds of life
        total_healing_received = 0
        total_damage_taken_last_4s = 0
        for ev in recap_events:
            ev_ts = ev["timestamp"]
            if ev_ts >= timestamp - 4000:
                if ev["type"] == "heal":
                    total_healing_received += ev["amount"]
                elif ev["type"] == "damage":
                    total_damage_taken_last_4s += ev["amount"]

        # Calculate unused available defensives at the moment of death
        unused_defensives = []
        for pd in personal_defensives:
            spell_id = pd["spell_id"]
            cooldown_ms = pd["cooldown_seconds"] * 1000
            
            # Find casts of this spell by the player before the death
            casts_before_death = [t for t in defensive_casts[spell_id] if t < timestamp]
            
            is_available = False
            if not casts_before_death:
                is_available = True
            else:
                last_cast = max(casts_before_death)
                if timestamp - last_cast >= cooldown_ms:
                    is_available = True
            
            if is_available:
                # Make sure they didn't cast it in the final 8 seconds (if they did, they used it)
                used_recently = any(timestamp - 8000 <= t <= timestamp for t in casts_before_death)
                if not used_recently:
                    unused_defensives.append({
                        "spell_id": spell_id,
                        "name": pd["name"],
                        "cooldown_seconds": pd["cooldown_seconds"]
                    })

        # Calculate unused consumables (Healthstone, Potions) at the moment of death
        unused_consumables = []
        has_unused_healthstone = not any(t < timestamp for t in healthstone_casts)
        has_unused_potion = not any(t < timestamp for t in potion_casts)
        
        if has_unused_healthstone:
            unused_consumables.append("Healthstone")
        if has_unused_potion:
            unused_consumables.append("Health Potion")

        # Compile Plain-English, 100% concrete summary
        summary_parts = []
        if total_avoidable_dmg > 0:
            avoidable_list_str = ", ".join(sorted(avoidable_names))
            summary_parts.append(f"Took {total_avoidable_dmg:,} avoidable damage in final 8s ({avoidable_list_str}).")

        unused_items = []
        for d in unused_defensives:
            unused_items.append(d["name"])
        for c in unused_consumables:
            unused_items.append(c)

        if unused_items:
            summary_parts.append(f"Died with {', '.join(unused_items)} available but unused.")

        if total_damage_taken_last_4s > 0:
            ratio_pct = (total_healing_received / total_damage_taken_last_4s) * 100
            if total_healing_received == 0:
                summary_parts.append(f"Received 0 healing in the final 4s while taking {total_damage_taken_last_4s:,} damage.")
            elif ratio_pct < 20:
                summary_parts.append(f"Received only {total_healing_received:,} healing (covering {round(ratio_pct)}% of damage) in final 4s while taking {total_damage_taken_last_4s:,} damage.")

        if not summary_parts:
            summary_parts.append("Died to unavoidable damage with no available defensives or consumables.")

        summary_text = " ".join(summary_parts)

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
                "recap": recap_events,
                "recap_analysis": {
                    "avoidable_damage_taken": total_avoidable_dmg,
                    "avoidable_damage_details": avoidable_damage_hits,
                    "healing_received": total_healing_received,
                    "damage_taken_last_4s": total_damage_taken_last_4s,
                    "unused_defensives": unused_defensives,
                    "unused_consumables": unused_consumables,
                    "summary": summary_text
                }
            }
        )

    return {
        "death_count": len(death_events),
        "death_events": death_events,
    }