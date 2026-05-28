# shortparse/server/ai_coach.py

import json
import logging
import requests
from shortparse.settings import GEMINI_API_KEY

logger = logging.getLogger(__name__)

def package_fight_context(analysis: dict) -> str:
    """
    Packs fight analysis metrics into a dense, structured context payload for the LLM.
    """
    fight = analysis.get("fight", {})
    scorecard = analysis.get("scorecard", [])
    mechanics = analysis.get("mechanics", {}).get("raid_mechanics", {})
    defensive_calibrator = analysis.get("defensive_calibrator", {})
    
    boss_name = fight.get("name", "Unknown Boss")
    kill_status = "Kill" if fight.get("kill") else f"Wipe (Boss at {fight.get('boss_percentage') or '?'}% HP)"
    
    # Roster Performance
    roster_lines = []
    for row in scorecard[:15]: # Limit to top 15 to conserve prompt tokens
        player = row.get("player")
        spec = row.get("spec", "Unknown")
        grade = row.get("grade", "C")
        role = row.get("role", "DPS")
        
        # Pull performance metrics
        metrics = analysis.get("player_metrics", {}).get(player, {}).get("performance", {})
        output = f"DPS: {metrics.get('dps', 0):,}" if role == "DPS" else f"HPS: {metrics.get('hps', 0):,}"
        avoidable = f"Avoidable Damage Taken: {metrics.get('avoidable_damage_taken', 0):,}"
        
        roster_lines.append(f"- {player} ({spec} - {role}): Grade {grade} | {output} | {avoidable}")
        
    # Mechanic Failures
    mechanic_lines = []
    for m_name, m_data in list(mechanics.items())[:5]: # Top 5 mechanics
        hits = m_data.get("hits", 0)
        worst_player = m_data.get("worst_player", "None")
        worst_hits = m_data.get("worst_hits", 0)
        mechanic_lines.append(f"- {m_name}: {hits} total hits. Worst failure: {worst_player} (hit {worst_hits} times)")
        
    # Defensive Cooldown Audits
    overlaps = defensive_calibrator.get("overlaps", [])
    dry_spells = defensive_calibrator.get("dry_spells", [])
    
    overlap_lines = [f"- {o.get('summary')} (Overhealing estimate: {o.get('overhealing_pct')}%)" for o in overlaps[:3]]
    dry_lines = [f"- {d.get('summary')}" for d in dry_spells[:3]]

    context = f"""
You are the elite "Raid Coach", an AI assistant designed to help World of Warcraft raid officers and players analyze combat logs.
Here is the structured data for this boss pull:

Boss Encounter: {boss_name}
Result: {kill_status}
Duration: {fight.get('duration_seconds', 0)} seconds

Roster Performance & Grades:
{"\n".join(roster_lines)}

Top Roster Mechanic Failures:
{"\n".join(mechanic_lines) if mechanic_lines else "None recorded."}

Healer Cooldown Overlaps (Wasteful concurrent raid CDs):
{"\n".join(overlap_lines) if overlap_lines else "None detected. Healers rotated cooldowns perfectly."}

Defensive Dry Spells (Dangerous periods of high damage with no active CDs):
{"\n".join(dry_lines) if dry_lines else "None detected. Heavy damage windows were fully covered."}

INSTRUCTIONS:
1. Ground your answers strictly in the metrics above.
2. Be encouraging but highly analytical.
3. Suggest concrete actions (e.g. "Move player X's cooldown to cover the dry spell", "Tell player Y to focus on dodging Z").
4. Keep your responses concise (max 3 short paragraphs).
5. Pay close attention to the Pull Result (Kill vs Wipe). If the fight was a Kill, do not talk about "why we wiped" or "preventing wipes"; instead, focus on optimizing performance, reducing avoidable damage, and cleaning up rotations for subsequent farm clears.
"""
    return context


def mock_coach_response(user_query: str, analysis: dict) -> str:
    """
    Rule-based mock AI Coach response to ensure premium functionality operates perfectly
    even without a configured GEMINI_API_KEY.
    """
    query = user_query.lower()
    fight = analysis.get("fight", {})
    boss_name = fight.get("name", "the boss")
    scorecard = analysis.get("scorecard", [])
    defensive_calibrator = analysis.get("defensive_calibrator", {})
    
    # Identify key players
    worst_players = [row.get("player") for row in scorecard if row.get("grade") in ("D", "F")]
    best_players = [row.get("player") for row in scorecard if row.get("grade") in ("S", "A")]
    
    overlaps = defensive_calibrator.get("overlaps", [])
    dry_spells = defensive_calibrator.get("dry_spells", [])
    
    is_kill = fight.get("kill", False)

    if "wipe" in query or "why did we" in query or "pull" in query or "catalyst" in query:
        if is_kill:
            response = f"**Raid Coach Analysis:** This pull on **{boss_name}** was actually a successful **Kill**! While you defeated the boss, there are key areas to optimize and clean up for smoother, lower-stress farm clears in the future:\n\n"
            if worst_players:
                response += f"Avoidable damage taken was a bit high. Players like **{', '.join(worst_players[:2])}** were hit repeatedly by avoidable boss spells. Dodging these mechanics more consistently will make subsequent farm kills much cleaner.\n\n"
            if dry_spells:
                response += f"Additionally, there was a **Defensive Dry Spell** at {dry_spells[0]['time_range']} taking {dry_spells[0]['damage_taken']:,} raid damage. Resolving these cooldown transitions will prevent panic scenarios during farm runs."
            else:
                response += "Our defensive rotations were relatively stable, so the focus should purely be on refining individual positioning and rotational efficiency."
        else:
            response = f"**Raid Coach Analysis:** On our pull of **{boss_name}**, the main points of failure were repeated avoidable mechanic hits and healing execution gaps.\n\n"
            if worst_players:
                response += f"Dodging needs to stabilize. Players like **{', '.join(worst_players[:2])}** were hit repeatedly by avoidable boss spells. Fixing these personal mistakes will prevent early deaths.\n\n"
            if dry_spells:
                response += f"Additionally, we had a major **Defensive Dry Spell** at {dry_spells[0]['time_range']} taking {dry_spells[0]['damage_taken']:,} raid damage. We need to assign a defensive cooldown like *Rallying Cry* or *Aura Mastery* here."
            else:
                response += "Our defensive rotations were relatively stable, so the focus should purely be on individual execution and survivability on the next pull."
        return response
        
    elif "heal" in query or "cooldown" in query or "overlap" in query or "dry" in query:
        if overlaps or dry_spells:
            response = "**Raid Coach Healing Audit:** I analyzed your healer cooldown rotation and found key opportunities to optimize:\n\n"
            if overlaps:
                response += f"1. **Cooldown Overlaps:** At {overlaps[0]['time_range']}, multiple raid cooldowns were active at once. We should spread these out.\n"
            if dry_spells:
                response += f"2. **Dry Spells:** We took heavy raid damage at {dry_spells[0]['time_range']} with zero cooldowns active. Assign a major heal there.\n"
            return response
        return "Our healer cooldown rotation was exceptionally clean! No wasteful overlaps or dangerous dry spell gaps were logged for this pull. Great job healers!"
        
    elif "who died" in query or "death" in query or "first" in query:
        if worst_players:
            return f"**Death Catalyst Audit:** The earliest deaths on **{boss_name}** were heavily influenced by avoidable damage. **{worst_players[0]}** took several unmitigated mechanic hits before going down. Dodge training is highly recommended."
        return f"Deaths were well-managed on **{boss_name}** until the final wipe phase. Keep up the high level of individual positioning!"
        
    else:
        # Generic premium fallback response
        best_str = f"**{best_players[0]}** (Grade {scorecard[0].get('grade')})" if best_players else "our top DPS"
        return f"**Raid Coach:** Welcome! I am reviewing the **{boss_name}** log files.\n\nOur standout performer was definitely {best_str} who played exceptionally clean. On the flip side, we had some rotation overlaps. Let me know if you want me to list specific mechanical failures or healer adjustments!"


def ask_gemini_coach(user_query: str, analysis: dict, custom_key: str | None = None) -> str:
    """
    Sends the packaged combat log context and the user query to the Gemini Free Tier API.
    If no GEMINI_API_KEY (and no custom_key) is configured, falls back gracefully to the mock rule engine.
    """
    api_key = custom_key or GEMINI_API_KEY
    if not api_key:
        logger.warning("No Gemini API key available. Falling back to Mock Coach engine.")
        return mock_coach_response(user_query, analysis)

    try:
        context = package_fight_context(analysis)
        
        # Google AI Studio Gemini API Endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": context + f"\nUser Query: {user_query}\n\nAI Response:"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 400
            }
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=12)
        
        if response.status_code == 200:
            result = response.json()
            candidates = result.get("candidates", [])
            if candidates:
                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text:
                    return text.strip()
            logger.error("Gemini API response missing content: %s", response.text)
        else:
            logger.error("Gemini API error (Status %s): %s", response.status_code, response.text)
            
    except Exception as e:
        logger.error("Failed to query Gemini API: %s", e)
        
    # Ultimate fallback to mock
    return mock_coach_response(user_query, analysis)
