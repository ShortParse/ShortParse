# shortparse/metrics/calibrator.py

from shortparse.metrics.timeline import format_fight_time, build_actor_lookup

MAJOR_DEFENSIVE_CDS = {
    31821: {"name": "Aura Mastery", "duration": 8, "class": "Paladin"},
    98008: {"name": "Spirit Link Totem", "duration": 6, "class": "Shaman"},
    108280: {"name": "Healing Tide Totem", "duration": 10, "class": "Shaman"},
    740: {"name": "Tranquility", "duration": 8, "class": "Druid"},
    64843: {"name": "Divine Hymn", "duration": 8, "class": "Priest"},
    115310: {"name": "Revival", "duration": 2, "class": "Monk"},
    51052: {"name": "Anti-Magic Zone", "duration": 10, "class": "Death Knight"},
    62618: {"name": "Power Word: Barrier", "duration": 10, "class": "Priest"},
    97462: {"name": "Rallying Cry", "duration": 10, "class": "Warrior"},
    206803: {"name": "Darkness", "duration": 8, "class": "Demon Hunter"},
}

def calculate_defensive_calibrator(
    fight: dict,
    events: list[dict],
    roster: list[dict],
    fight_data: dict = None,
) -> dict:
    fight_start = fight["startTime"]
    duration_s = max(1.0, (fight["endTime"] - fight_start) / 1000)
    duration_idx = int(duration_s) + 2

    # 1. Build Actor Lookup for resolving players
    actor_lookup = build_actor_lookup(roster)

    # 2. Build Ability Lookup from masterData to resolve raw WCL spell IDs to names
    ability_lookup = {}
    master_data = fight_data.get("masterData", {}) if fight_data else {}
    for ability in master_data.get("abilities", []):
        a_id = ability.get("gameID")
        a_name = ability.get("name")
        if a_id is not None and a_name:
            ability_lookup[a_id] = a_name

    # 3. Track Raid Damage Taken Per Second (DTPS)
    raid_dtps = [0] * duration_idx
    boss_spells_at_second = {}  # second -> {spell_name -> amount}

    for event in events:
        if event.get("type") != "damage":
            continue

        ts = event.get("timestamp")
        if ts is None:
            continue

        elapsed = int((ts - fight_start) / 1000)
        if 0 <= elapsed < len(raid_dtps):
            amount = int(event.get("amount") or 0)
            absorbed = int(event.get("absorbed") or 0)
            total_hit = amount + absorbed

            raid_dtps[elapsed] += total_hit

            # Track which spell contributed the hit, resolving through masterData first
            spell_id = event.get("abilityGameID")
            spell_name = None
            if spell_id in ability_lookup:
                spell_name = ability_lookup[spell_id]
            else:
                ability = event.get("ability")
                if isinstance(ability, dict):
                    spell_name = ability.get("name")
                elif isinstance(ability, str):
                    spell_name = ability
                else:
                    spell_name = event.get("abilityName") or event.get("name") or "Unknown Boss Attack"

            if elapsed not in boss_spells_at_second:
                boss_spells_at_second[elapsed] = {}
            
            boss_spells_at_second[elapsed][spell_name] = boss_spells_at_second[elapsed].get(spell_name, 0) + total_hit

    # 4. Track All Major Defensive Casts
    defensive_casts = []
    for event in events:
        if event.get("type") != "cast":
            continue

        spell_id = event.get("abilityGameID")
        if spell_id not in MAJOR_DEFENSIVE_CDS:
            continue

        ts = event.get("timestamp")
        if ts is None:
            continue

        source_id = event.get("sourceID")
        player_name = actor_lookup.get(source_id, "Unknown Player")

        elapsed_s = (ts - fight_start) / 1000
        cd_info = MAJOR_DEFENSIVE_CDS[spell_id]

        defensive_casts.append({
            "spell_id": spell_id,
            "spell_name": cd_info["name"],
            "player": player_name,
            "class": cd_info["class"],
            "start_seconds": round(elapsed_s, 1),
            "duration": cd_info["duration"],
        })

    # 5. Scan for Major Damage Spikes (Local Peaks)
    spikes = []
    avg_dtps = sum(raid_dtps) / max(1.0, duration_s)
    
    # Threshold is adaptive: at least 3.5x the average DTPS, and a minimum baseline of 500k raw damage
    spike_threshold = max(3.5 * avg_dtps, 500000.0)

    # Prevent multiple rolling ticks in a row from counting as individual spikes by using a cooldown window (5 seconds)
    last_spike_seconds = -10

    for t in range(2, len(raid_dtps) - 2):
        # 2-second rolling damage total
        rolling_damage = raid_dtps[t] + raid_dtps[t - 1]

        if rolling_damage >= spike_threshold:
            # Local peak check: must be greater than or equal to adjacent seconds
            prev_rolling = raid_dtps[t - 1] + raid_dtps[t - 2]
            next_rolling = raid_dtps[t + 1] + raid_dtps[t]
            
            if rolling_damage >= prev_rolling and rolling_damage >= next_rolling:
                if t - last_spike_seconds >= 5:
                    # Find the boss spell that caused the most damage in this second or the previous second
                    spells = {}
                    for sec in (t - 1, t):
                        if sec in boss_spells_at_second:
                            for spell, val in boss_spells_at_second[sec].items():
                                spells[spell] = spells.get(spell, 0) + val
                    
                    major_spell = "Raid-Wide Pulse"
                    if spells:
                        major_spell = max(spells, key=spells.get)

                    # Check if any raid defensive was active during this rolling 2-second window
                    active_cds = []
                    for cast in defensive_casts:
                        # Cooldown overlaps if its cast interval [start, start + duration] overlaps with [t-2, t]
                        cast_start = cast["start_seconds"]
                        cast_end = cast_start + cast["duration"]
                        if not (cast_end < t - 2 or cast_start > t):
                            active_cds.append(cast)

                    spikes.append({
                        "time": format_fight_time(fight_start + t * 1000, fight_start),
                        "seconds": t,
                        "amount": rolling_damage,
                        "spell_name": major_spell,
                        "active_cooldowns": active_cds,
                        "covered": len(active_cds) > 0,
                    })
                    last_spike_seconds = t

    return {
        "timeline": raid_dtps,
        "casts": defensive_casts,
        "spikes": spikes,
    }
