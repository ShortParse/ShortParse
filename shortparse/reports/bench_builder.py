import requests
from shortparse.settings import GEMINI_API_KEY
from shortparse.reports.tracker import get_slump_tracker_analytics

UTILITY_MAP = {
    # Class-specific utility mappings
    "Death Knight": {"br": True, "immunity": True, "buff": "Abomination Limb / AMZ"},
    "Demon Hunter": {"buff": "Chaos Brand (5% Magic Damage)"},
    "Druid": {"br": True, "buff": "Mark of the Wild (3% Versatility)", "speed": True},
    "Evoker": {"lust": True, "buff": "Blessing of the Bronze (Cooldown Recovery)"},
    "Hunter": {"lust": True, "immunity": True, "buff": "Sentinel Owl"},
    "Mage": {"lust": True, "immunity": True, "buff": "Arcane Intellect (5% Intellect)"},
    "Monk": {"buff": "Generous Pour / Mystic Touch (5% Physical Damage)"},
    "Paladin": {"br": True, "immunity": True, "buff": "Devotion Aura (3% Damage Reduction)"},
    "Priest": {"buff": "Power Word: Fortitude (5% Stamina)"},
    "Rogue": {"immunity": True, "buff": "Atrophic Poison (3% Boss Damage Reduction)"},
    "Shaman": {"lust": True, "speed": True, "buff": "Windfury Totem / Mana Spring"},
    "Warlock": {"br": True, "buff": "Demonic Gateway / Healthstones"},
    "Warrior": {"buff": "Battle Shout (5% Attack Power)"}
}

BOSS_REQUIREMENTS = {
    # Encounter ID maps to special requirement tags
    3182: {"name": "Crown of the Cosmos", "needs": ["immunity", "speed"]},
    3183: {"name": "Midnight Falls", "needs": ["lust", "br"]},
    3184: {"name": "Imperator Averzian", "needs": ["immunity", "br"]},
    3185: {"name": "Vorasius", "needs": ["speed"]},
    3186: {"name": "Fallen-King Salhadaar", "needs": ["immunity"]},
    3187: {"name": "Vaelgor & Ezzorak", "needs": ["br"]},
    3188: {"name": "Lightblinded Vanguard", "needs": ["speed"]}
}

def generate_gemini_directive(boss_name: str, roster_20: list, bench: list) -> str:
    """
    Calls the Gemini API to write a positive and constructive roster composition directive.
    """
    if not GEMINI_API_KEY:
        return (
            f"Raid composition optimized for high utility on {boss_name}. "
            "Roster utilizes balanced raid-wide defensive coverage and cooldowns to counter "
            "the encounter's main mechanics. Keep focus high and execute clean movement!"
        )
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = (
        f"You are a supportive, positive WoW Raid Coach. Given the recommended 20-man raid team composition "
        f"and the benched list for the boss '{boss_name}', write a short 2-3 sentence strategic directive. "
        f"Use a highly positive, constructive tone. Frame the benching decisions around raid-wide utility, "
        f"encourage player rotation, and do not criticize or belittle any players.\n"
        f"Roster: {', '.join(p['name'] for p in roster_20)}\n"
        f"Bench: {', '.join(p['name'] for p in bench)}\n"
    )
    
    try:
        response = requests.post(
            url,
            json={"contents": [{"parts": [{"text": prompt}]}]},
            headers={"Content-Type": "application/json"},
            timeout=8
        )
        if response.status_code == 200:
            payload = response.json()
            return payload["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        pass
        
    return (
        f"Raid composition optimized for high utility on {boss_name}. "
        "Roster utilizes balanced raid-wide defensive coverage and cooldowns to counter "
        "the encounter's main mechanics. Keep focus high and execute clean movement!"
    )

def build_roster_composition(encounter_id: int, player_names: list[str]) -> dict:
    """
    Assembles the optimal 20-man roster from available players based on role requirements,
    historical grades, and boss-specific utility.
    """
    # 1. Fetch historical analytics to grade players
    analytics = get_slump_tracker_analytics()
    players_data = {p["name"]: p for p in analytics.get("players", [])}
    
    boss_info = BOSS_REQUIREMENTS.get(encounter_id, {"name": "Raid Boss", "needs": []})
    boss_name = boss_info["name"]
    needs = boss_info["needs"]
    
    # Grade mapping for scoring
    grade_points = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
    
    # 2. Build candidates list with scores
    candidates = []
    for name in player_names:
        p_data = players_data.get(name)
        if p_data:
            grade = p_data.get("avg_grade", "C")
            class_name = p_data.get("class", "Unknown")
            role = p_data.get("role", "DPS")
        else:
            grade = "C"
            class_name = "Unknown"
            role = "DPS"
            
        score = grade_points.get(grade, 2) * 10
        
        # Add utility bonuses
        utility = UTILITY_MAP.get(class_name, {})
        for need in needs:
            if utility.get(need):
                score += 15  # Heavy bonus for meeting encounter specific needs
                
        candidates.append({
            "name": name,
            "class": class_name,
            "role": role,
            "grade": grade,
            "score": score
        })
        
    # Sort candidates by score descending
    candidates.sort(key=lambda x: -x["score"])
    
    # 3. Assemble 20-man team (2 Tanks, 4-5 Healers, rest DPS)
    tanks = [c for c in candidates if c["role"] == "Tank"]
    healers = [c for c in candidates if c["role"] == "Healer"]
    dps = [c for c in candidates if c["role"] in ("DPS", "Melee DPS", "Ranged DPS", "Unknown")]
    
    selected_tanks = tanks[:2]
    selected_healers = healers[:4]
    
    # Fill remaining spots with DPS and remaining healers/tanks based on score
    remaining_spots = 20 - len(selected_tanks) - len(selected_healers)
    pool = dps + tanks[2:] + healers[4:]
    pool.sort(key=lambda x: -x["score"])
    
    selected_pool = pool[:remaining_spots]
    
    final_roster_list = selected_tanks + selected_healers + selected_pool
    bench_pool = pool[remaining_spots:]
    
    # Format roster details
    formatted_roster = []
    for p in final_roster_list:
        class_name = p["class"]
        utils = UTILITY_MAP.get(class_name, {})
        formatted_roster.append({
            "name": p["name"],
            "class": class_name,
            "role": p["role"],
            "grade": p["grade"],
            "utility": ", ".join(k for k, v in utils.items() if v is True) or utils.get("buff", "General DPS")
        })
        
    # Format bench details (with supportive explanations)
    formatted_bench = []
    for p in bench_pool:
        class_name = p["class"]
        formatted_bench.append({
            "name": p["name"],
            "class": class_name,
            "role": p["role"],
            "grade": p["grade"],
            "reason": f"Roster rotation to optimize encounter-specific utility and buffs on {boss_name}. Positioned as primary backup."
        })
        
    # Generate directive
    directive = generate_gemini_directive(boss_name, formatted_roster, formatted_bench)
    
    return {
        "boss_name": boss_name,
        "encounter_id": encounter_id,
        "roster": formatted_roster,
        "bench": formatted_bench,
        "ai_directive": directive
    }
