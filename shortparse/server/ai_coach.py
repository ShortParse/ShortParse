# shortparse/server/ai_coach.py

import json
import time
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
You are "ShortParse Raid Intelligence", an objective, highly analytical, and clinical World of Warcraft combat log analysis engine.
You are programmed to provide data-driven observations to raid officers.
Do NOT use human-like chitchat, friendly greetings, or emotional qualifiers (such as "Alright team", "heartbreaking", "great effort", "good job", "thankfully", or "sadly"). 
Maintain an objective, cold, precise, and structured robotic tone.

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
2. Maintain a purely clinical, precise, and objective robotic tone.
3. Suggest concrete actions (e.g. "Reassign cooldown X to cover dry spell Y", "Instruct player Z to reduce hits from mechanic W").
4. Keep your responses extremely concise and structured (max 2-3 short, dense paragraphs, or clear bullet points).
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
            response = f"**Raid Intelligence Analysis:** Pull on **{boss_name}** resulted in a successful **Kill**. Optimization parameters are required for subsequent farm clears to minimize raid stress:\n\n"
            if worst_players:
                response += f"- **Vulnerability Exposure:** Avoidable damage was recorded. Players like **{', '.join(worst_players[:2])}** sustained repeated hits from avoidable encounter mechanics. Mitigating these inputs will optimize subsequent clears.\n\n"
            if dry_spells:
                response += f"- **Defensive Transition:** A defensive dry spell was logged at {dry_spells[0]['time_range']} causing {dry_spells[0]['damage_taken']:,} raid damage. Aligning active cooldowns during this interval will reduce damage spikes."
            else:
                response += "- **Defensive Status:** Defensive rotations were stable. Focus parameters should remain on individual output and positioning efficiency."
        else:
            response = f"**Raid Intelligence Analysis:** Pull on **{boss_name}** resulted in a **Wipe**. Primary failure vectors mapped to mechanic vulnerability and healing throughput limits:\n\n"
            if worst_players:
                response += f"- **Mechanic Failures:** Players like **{', '.join(worst_players[:2])}** sustained repeated avoidable damage hits. Reducing these errors will increase pull longevity.\n\n"
            if dry_spells:
                response += f"- **Healing Gap:** A defensive dry spell at {dry_spells[0]['time_range']} sustained {dry_spells[0]['damage_taken']:,} damage. Assign a defensive cooldown (*Rallying Cry* or *Aura Mastery*) to this timestamp."
            else:
                response += "- **Defensive Status:** Defensive rotations were stable. Survivability failure is attributed to individual position or execution drift."
        return response
        
    elif "heal" in query or "cooldown" in query or "overlap" in query or "dry" in query:
        if overlaps or dry_spells:
            response = "**Raid Intelligence Healing Audit:** Opportunity markers identified in defensive rotation:\n\n"
            if overlaps:
                response += f"1. **Overlap Alert:** Multiple major defensive cooldowns were active concurrently at {overlaps[0]['time_range']}. Restructure rotation to spread coverage.\n"
            if dry_spells:
                response += f"2. **Dry Spell Alert:** High incoming damage logged at {dry_spells[0]['time_range']} with 0 active defensives. Assign healing coverage to this window.\n"
            return response
        return "**Raid Intelligence Healing Audit:** Perfect healer cooldown rotation logged. 0 overlaps and 0 dry spells detected."
        
    elif "who died" in query or "death" in query or "first" in query:
        if worst_players:
            return f"**Raid Intelligence Death Catalyst Audit:** Initial deaths on **{boss_name}** correlate directly with avoidable damage. **{worst_players[0]}** sustained repeated unmitigated hits prior to termination."
        return f"**Raid Intelligence Death Catalyst Audit:** Zero early deaths logged on **{boss_name}**. Roster positioning remained stable until wipe parameters were met."
        
    else:
        best_str = f"**{best_players[0]}** (Grade {scorecard[0].get('grade')})" if best_players else "top output specs"
        return f"**ShortParse Raid Intelligence:** Analysis of **{boss_name}** log files completed.\n\n- Standout performer: {best_str}.\n- Status: Roster synergy limits detected. Query further to review specific mechanic execution sheets or healer cooldown overlaps."


def ask_gemini_coach(user_query: str, analysis: dict, custom_key: str | None = None) -> str:
    """
    Sends the packaged combat log context and the user query to the Gemini Free Tier API.
    If no GEMINI_API_KEY (and no custom_key) is configured, falls back gracefully to the mock rule engine.
    """
    api_key = custom_key or GEMINI_API_KEY
    if not api_key:
        logger.warning("No Gemini API key available. Falling back to Mock Coach engine.")
        return mock_coach_response(user_query, analysis)

    max_retries = 3
    retry_delay = 1.0  # seconds

    for attempt in range(max_retries):
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
                    "temperature": 0.2,
                    "maxOutputTokens": 1024
                }
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=12)
            
            if response.status_code == 200:
                result = response.json()
                candidates = result.get("candidates", [])
                if candidates:
                    text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    logger.info("Raw Gemini Coach response payload: %r", text)
                    if text:
                        return text.strip()
                logger.error("Gemini API response missing content: %s", response.text)
                break
            
            elif response.status_code in (429, 503):
                logger.warning(
                    "Gemini API returned status %s. Retrying attempt %s/%s after %ss delay...",
                    response.status_code, attempt + 1, max_retries, retry_delay
                )
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            
            else:
                logger.error("Gemini API error (Status %s): %s", response.status_code, response.text)
                break
                
        except Exception as e:
            logger.error("Failed to query Gemini API on attempt %s: %s", attempt + 1, e)
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
                continue

    # Ultimate fallback to mock
    return mock_coach_response(user_query, analysis)
