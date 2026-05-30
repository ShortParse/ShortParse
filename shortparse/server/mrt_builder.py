# shortparse/server/mrt_builder.py

import logging

logger = logging.getLogger(__name__)

# Normalize class names to lowercase keys with no spaces
COOLDOWNS_BY_SPEC = {
    ("paladin", "holy"): [{"name": "Aura Mastery", "spell_id": 31821, "cooldown": 180, "type": "healer"}],
    ("druid", "restoration"): [{"name": "Tranquility", "spell_id": 740, "cooldown": 180, "type": "healer"}],
    ("priest", "holy"): [{"name": "Divine Hymn", "spell_id": 64843, "cooldown": 180, "type": "healer"}],
    ("priest", "discipline"): [{"name": "Power Word: Barrier", "spell_id": 62618, "cooldown": 180, "type": "healer"}],
    ("shaman", "restoration"): [
        {"name": "Spirit Link Totem", "spell_id": 98008, "cooldown": 180, "type": "healer"},
        {"name": "Healing Tide Totem", "spell_id": 108280, "cooldown": 180, "type": "healer"}
    ],
    ("monk", "mistweaver"): [{"name": "Revival", "spell_id": 115310, "cooldown": 180, "type": "healer"}],
}

COOLDOWNS_BY_CLASS = {
    "warrior": [{"name": "Rallying Cry", "spell_id": 97462, "cooldown": 180, "type": "utility"}],
    "deathknight": [{"name": "Anti-Magic Zone", "spell_id": 51052, "cooldown": 120, "type": "utility"}],
    "demonhunter": [{"name": "Darkness", "spell_id": 206803, "cooldown": 180, "type": "utility"}],
    "death knight": [{"name": "Anti-Magic Zone", "spell_id": 51052, "cooldown": 120, "type": "utility"}],
    "demon hunter": [{"name": "Darkness", "spell_id": 206803, "cooldown": 180, "type": "utility"}],
}

def get_player_cooldowns(player: dict) -> list[dict]:
    """
    Returns the list of raid defensive cooldowns a player possesses based on class and spec.
    """
    cls = (player.get("class") or "").strip().lower()
    spec = (player.get("spec") or "").strip().lower()
    
    # 1. Try spec-specific first
    if (cls, spec) in COOLDOWNS_BY_SPEC:
        return COOLDOWNS_BY_SPEC[(cls, spec)]
        
    # 2. Try class fallback
    if cls in COOLDOWNS_BY_CLASS:
        return COOLDOWNS_BY_CLASS[cls]
        
    return []

def generate_mrt_notes(roster: list[dict], spikes: list[dict]) -> str:
    """
    Dynamically maps available roster cooldowns to boss damage spikes.
    Outputs a copy-pasteable note formatted for Method Raid Tools (MRT) or Angry Assignments.
    """
    # Build a list of players in the raid with raid defensives
    raid_cooldown_players = []
    for player in roster:
        cds = get_player_cooldowns(player)
        if cds:
            for cd in cds:
                raid_cooldown_players.append({
                    "name": player["name"],
                    "class": player["class"],
                    "spec": player["spec"],
                    "cd": cd,
                    "last_used": -999 # seconds
                })
                
    # Sort cooldown players: healers first, then utility
    raid_cooldown_players.sort(key=lambda p: 0 if p["cd"]["type"] == "healer" else 1)
    
    lines = []
    lines.append("; --- ShortParse Premium: Automated Cooldown Notes ---")
    lines.append("; Copy and paste this directly into Method Raid Tools / Angry Assignments")
    lines.append("")
    
    for spike in spikes:
        # Skip spikes that are explicitly marked as non-MRT
        if spike.get("mrt") is False:
            continue

        seconds = spike.get("seconds") or 0
        spell_name = spike.get("spell_name") or "Raid Damage Spike"
        
        # Format time to MM:SS
        min_val = seconds // 60
        sec_val = seconds % 60
        time_str = f"{min_val:02d}:{sec_val:02d}"
        
        lines.append(f"{{time:{time_str}}} -- {spell_name} --")
        
        # Try to assign up to one healer CD and one utility CD if the spike is large,
        # or just the first available cooldown.
        assigned_any = False
        
        # A. Find available healer CD
        healer_cd = None
        for p in raid_cooldown_players:
            if p["cd"]["type"] != "healer":
                continue
            cooldown_length = p["cd"]["cooldown"]
            if seconds - p["last_used"] >= cooldown_length:
                healer_cd = p
                break
                
        if healer_cd:
            healer_cd["last_used"] = seconds
            lines.append(f"{{time:{time_str}}}   {healer_cd['name']} ({healer_cd['cd']['name']})")
            assigned_any = True
            
        # B. Find available utility CD
        utility_cd = None
        for p in raid_cooldown_players:
            if p["cd"]["type"] != "utility":
                continue
            cooldown_length = p["cd"]["cooldown"]
            if seconds - p["last_used"] >= cooldown_length:
                utility_cd = p
                break
                
        if utility_cd:
            utility_cd["last_used"] = seconds
            lines.append(f"{{time:{time_str}}}   {utility_cd['name']} ({utility_cd['cd']['name']})")
            assigned_any = True
            
        # C. Fallback: if nothing assigned, and no healer CD was found, try to assign ANY CD
        if not assigned_any:
            fallback_cd = None
            for p in raid_cooldown_players:
                cooldown_length = p["cd"]["cooldown"]
                if seconds - p["last_used"] >= cooldown_length:
                    fallback_cd = p
                    break
            if fallback_cd:
                fallback_cd["last_used"] = seconds
                lines.append(f"{{time:{time_str}}}   {fallback_cd['name']} ({fallback_cd['cd']['name']})")
            else:
                lines.append(f"{{time:{time_str}}}   [Assign Cooldown Here!]")
                
        lines.append("")
        
    return "\n".join(lines)
