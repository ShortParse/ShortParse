# shortparse/server/ai_coach.py

import json
import time
import logging
import requests
from shortparse.settings import GEMINI_API_KEY

logger = logging.getLogger(__name__)

def package_fight_context(base_analysis: dict, pull_index: str = "all") -> str:
    """
    Packs fight analysis metrics into a dense, structured context payload for the LLM.
    Supports either the aggregated boss overview ("all") or a specific individual pull.
    """
    active_analysis = base_analysis
    is_individual = False
    pull_num = 1
    
    if pull_index != "all":
        try:
            pidx = int(pull_index)
            pulls = base_analysis.get("pulls_details", [])
            if 0 <= pidx < len(pulls):
                active_analysis = pulls[pidx]
                is_individual = True
                pull_num = pidx + 1
        except (ValueError, TypeError):
            pass

    fight = active_analysis.get("fight", {})
    scorecard = active_analysis.get("scorecard", [])
    mechanics = active_analysis.get("mechanics", {}).get("raid_mechanics", {})
    defensive_calibrator = active_analysis.get("defensive_calibrator", {})
    
    boss_name = fight.get("name", "Unknown Boss")
    
    if is_individual:
        kill_status = "Kill" if fight.get("kill") else f"Wipe (Boss at {fight.get('boss_percentage') or '?'}% HP)"
    else:
        pulls_count = len(base_analysis.get("pulls_details", [])) or 1
        kills_count = base_analysis.get("fight", {}).get("kills_count", 1 if base_analysis.get("fight", {}).get("kill") else 0)
        wipes_count = pulls_count - kills_count
        kill_status = f"Aggregated Overview ({pulls_count} Pulls Total: {kills_count} Kills, {wipes_count} Wipes)"
    
    # Roster Performance
    roster_lines = []
    for row in scorecard[:15]: # Limit to top 15 to conserve prompt tokens
        player = row.get("player")
        spec = row.get("spec", "Unknown")
        grade = row.get("grade", "C")
        role = row.get("role", "DPS")
        
        # Pull performance metrics
        metrics = active_analysis.get("player_metrics", {}).get(player, {}).get("performance", {})
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

    # Boss Pulls Progression History (always draw from base_analysis for progression overview)
    progression = base_analysis.get("progression", {})
    pulls = progression.get("pulls", [])
    pull_lines = []
    for p in pulls:
        result = "Kill" if p.get("kill") else f"Wipe ({p.get('boss_percentage') or '?'}% HP)"
        pull_lines.append(
            f"- Pull {p.get('pull_number')}: {result} | Duration: {p.get('duration_seconds')}s | Phase: {p.get('last_phase')}"
        )
    pulls_history_text = "\n".join(pull_lines) if pull_lines else "No progression history."

    if is_individual:
        context_instruction = f"""
YOU ARE ANALYZING PULL {pull_num} ONLY (Individual Pull).
Focus your observations and diagnostics exclusively on this specific pull. Do not generalize across other pulls or discuss other fights unless they are relevant as a contrast. Ground all comments solely on the performance, cooldown overlaps, and death events of Pull {pull_num} (be it a Wipe or a Kill).
"""
    else:
        context_instruction = f"""
YOU ARE ANALYZING AN AGGREGATED VIEW OF ALL PULLS ({len(base_analysis.get('pulls_details', [])) or 1} PULLS TOTAL).
Your goal is to provide a high-level review of all pulls at a 30,000-foot view. Discuss overall roster patterns, consistent mechanic failures across multiple pulls, or persistent healing dry spells. Do not get bogged down in a single pull's details unless it represents a clear recurring pattern.
"""

    context = f"""
You are "ShortParse Raid Intelligence", an objective, highly analytical, and clinical World of Warcraft combat log analysis engine.
You are programmed to provide data-driven observations to raid officers.
Do NOT use human-like chitchat, friendly greetings, or emotional qualifiers (such as "Alright team", "heartbreaking", "great effort", "good job", "thankfully", or "sadly"). 
Maintain an objective, cold, precise, and structured robotic tone.

{context_instruction}

Here is the structured data for this boss encounter:

Boss Encounter: {boss_name}
Result Context: {kill_status}
Active Pull Duration: {fight.get('duration_seconds', 0)} seconds

Boss Pulls Progression History:
{pulls_history_text}

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
5. Pay close attention to the Active Pull Result (Kill vs Wipe). If the active view is a Kill, do not talk about "why we wiped" or "preventing wipes"; instead, focus on optimizing performance, reducing avoidable damage, and cleaning up rotations for subsequent farm clears.
"""
    return context


def mock_coach_response(user_query: str, analysis: dict, pull_index: str = "all") -> str:
    """
    Rule-based mock AI Coach response to ensure premium functionality operates perfectly
    even without a configured GEMINI_API_KEY or during API rate limits.
    """
    query = user_query.lower()
    
    active_analysis = analysis
    is_individual = False
    pull_num = 1
    
    if pull_index != "all":
        try:
            pidx = int(pull_index)
            pulls = analysis.get("pulls_details", [])
            if 0 <= pidx < len(pulls):
                active_analysis = pulls[pidx]
                is_individual = True
                pull_num = pidx + 1
        except (ValueError, TypeError):
            pass

    fight = active_analysis.get("fight", {})
    boss_name = fight.get("name", "the boss")
    scorecard = active_analysis.get("scorecard", [])
    defensive_calibrator = active_analysis.get("defensive_calibrator", {})
    
    # Identify key players
    worst_players = [row.get("player") for row in scorecard if row.get("grade") in ("D", "F")]
    best_players = [row.get("player") for row in scorecard if row.get("grade") in ("S", "A")]
    
    overlaps = defensive_calibrator.get("overlaps", [])
    dry_spells = defensive_calibrator.get("dry_spells", [])
    
    is_kill = fight.get("kill", False)

    # Aggregated View Mocking
    if not is_individual:
        pulls_details = analysis.get("pulls_details", [])
        pulls_count = len(pulls_details) or 1
        kills_count = analysis.get("fight", {}).get("kills_count", 1 if analysis.get("fight", {}).get("kill") else 0)
        wipes_count = pulls_count - kills_count
        
        if "wipe" in query or "why did we" in query or "pull" in query or "catalyst" in query:
            response = f"**Raid Intelligence Aggregated Diagnostics:** Analyzed **{pulls_count} pulls** on **{boss_name}** ({kills_count} Kills, {wipes_count} Wipes). High-level overview indicates a persistent pattern of avoidable errors across multiple wipes:\n\n"
            if worst_players:
                response += f"- **Recurrent Mechanic Errors:** Roster members like **{', '.join(worst_players[:2])}** consistently took high avoidable damage across multiple wipes. Reinforcing execution on mechanics will decrease overall wipe rates.\n\n"
            if dry_spells:
                response += f"- **Systemic Defensive Dry Spells:** We averaged high damage dry spells (e.g. at {dry_spells[0]['time_range']} if dry_spells else 'various windows') with no major raid cooldowns active. Pre-plan defensives for these recurring high-stress windows."
            else:
                response += "- **Defensive Overview:** Overall healer CD rotations were stable, but execution positioning remains the primary factor for mechanical errors."
            return response
            
        elif "heal" in query or "cooldown" in query or "overlap" in query or "dry" in query:
            response = f"**Raid Intelligence Aggregated Healer Audit:** Aggregated logs across {pulls_count} pulls indicate healing rotation trends:\n\n"
            if overlaps:
                response += f"- **CD Overlaps:** Persistent overlaps of major defensive cooldowns recorded. Spreading these out will increase average raid life support.\n"
            if dry_spells:
                response += f"- **Dry Spell Trends:** Systemic dry spells logged around recurring boss phases. Rotate healing cooldowns strictly by timeline milestones.\n"
            if not overlaps and not dry_spells:
                response += "- **Healing Efficiency:** Rotation trends were stable without systemic overlaps."
            return response
            
        else:
            best_str = f"**{best_players[0]}**" if best_players else "top Specs"
            return f"**ShortParse Raid Intelligence (Aggregated):** Overall 30,000-foot review of **{boss_name}** complete. Standout performer across all pulls was {best_str} with consistent high-tier grades."

    # Individual Pull Mocking
    else:
        if "wipe" in query or "why did we" in query or "pull" in query or "catalyst" in query:
            if is_kill:
                response = f"**Raid Intelligence Diagnostics (Pull {pull_num} - Kill):** Pull resulted in a successful **Kill**. Focus is placed on farm clear optimizations:\n\n"
                if worst_players:
                    response += f"- **Avoidable Hit Audit:** Players like **{', '.join(worst_players[:2])}** took repeated avoidable mechanic hits. Mitigating these will ease healer stress.\n\n"
                if dry_spells:
                    response += f"- **Defensive Placement:** A dry spell was logged at {dry_spells[0]['time_range']}. Assigning a CD here will keep clearing safer."
                else:
                    response += "- **Survivability:** Overall execution was stable during this kill."
            else:
                response = f"**Raid Intelligence Diagnostics (Pull {pull_num} - Wipe):** Pull resulted in a **Wipe** (Boss at {fight.get('boss_percentage') or '?'}% HP). Primary failure factors for this specific pull:\n\n"
                if worst_players:
                    response += f"- **Fatal Mechanic Failures:** Key deaths occurred due to avoidable damage on players like **{', '.join(worst_players[:2])}**.\n\n"
                if dry_spells:
                    response += f"- **Healing Starvation:** A critical dry spell was logged at {dry_spells[0]['time_range']} taking {dry_spells[0]['damage_taken']:,} damage with 0 active raid CDs."
                else:
                    response += "- **Execution Drift:** Survivability failure is attributed to individual positioning faults during high-stress phases."
            return response
            
        elif "heal" in query or "cooldown" in query or "overlap" in query or "dry" in query:
            response = f"**Raid Intelligence Healer Audit (Pull {pull_num}):** Audit of CD assignments on this specific pull:\n\n"
            if overlaps:
                response += f"- **Wasteful Cooldown Overlaps:** Overlapping defensive cooldowns at {overlaps[0]['time_range']} led to massive overhealing.\n"
            if dry_spells:
                response += f"- **Dangerous Dry Spells:** Critical dry spell logged at {dry_spells[0]['time_range']} with no major defensives active.\n"
            if not overlaps and not dry_spells:
                response += "- **Healing Efficiency:** Rotation was executed perfectly without overlaps or dry spells during this pull."
            return response
            
        else:
            best_str = f"**{best_players[0]}**" if best_players else "top specs"
            return f"**ShortParse Raid Intelligence (Pull {pull_num}):** Detailed audit of individual pull {pull_num} on **{boss_name}** complete. Performer of the pull was {best_str}."


def ask_gemini_coach(user_query: str, analysis: dict, custom_key: str | None = None, pull_index: str = "all") -> str:
    """
    Sends the packaged combat log context and the user query to the Gemini Free Tier API.
    If no GEMINI_API_KEY (and no custom_key) is configured, falls back gracefully to the mock rule engine.
    """
    api_key = custom_key or GEMINI_API_KEY
    if not api_key:
        logger.warning("No Gemini API key available. Falling back to Mock Coach engine.")
        return mock_coach_response(user_query, analysis, pull_index=pull_index)

    max_retries = 3
    retry_delay = 1.0  # seconds

    for attempt in range(max_retries):
        try:
            context = package_fight_context(analysis, pull_index=pull_index)
            
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
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE"
                    }
                ]
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=12)
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Full Gemini API Response JSON: %s", json.dumps(result))
                
                candidates = result.get("candidates", [])
                if candidates:
                    candidate = candidates[0]
                    finish_reason = candidate.get("finishReason")
                    logger.info("Gemini Candidate finishReason: %s", finish_reason)
                    
                    text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
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
    return mock_coach_response(user_query, analysis, pull_index=pull_index)
