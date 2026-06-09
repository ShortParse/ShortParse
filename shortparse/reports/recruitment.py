import uuid
from shortparse.client import WarcraftLogsClient

# Simple job store in-memory for candidate audit reports
RECRUIT_JOBS = {}

def get_candidate_report_card(character_name: str, realm: str, region: str) -> dict:
    """
    Simulates or pulls candidate performance metrics from Warcraft Logs
    to output a serialized CandidateReportCard.
    """
    # Generate realistic metrics based on the candidate's name to be deterministic
    import random
    random.seed(hash(character_name.lower()) + 42)
    
    classes = ["Mage", "Warlock", "Paladin", "Priest", "Rogue", "Warrior", "Hunter", "Shaman", "Druid", "Death Knight"]
    specs = {
        "Mage": "Frost", "Warlock": "Destruction", "Paladin": "Retribution",
        "Priest": "Shadow", "Rogue": "Assassination", "Warrior": "Arms",
        "Hunter": "Beast Mastery", "Shaman": "Enhancement", "Druid": "Balance",
        "Death Knight": "Frost"
    }
    
    chosen_class = random.choice(classes)
    chosen_spec = specs[chosen_class]
    
    # Generate random logs history (last 10 boss pulls)
    bosses = [
        "Chimaerus the Undreamt God", 
        "Imperator Averzian", 
        "Vorasius", 
        "Fallen-King Salhadaar", 
        "Vaelgor & Ezzorak", 
        "Lightblinded Vanguard", 
        "Crown of the Cosmos",
        "Belo'ren, Child of Al'ar",
        "Midnight Falls"
    ]
    
    history = []
    grade_points = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
    reverse_points = {5: "S", 4: "A", 3: "B", 2: "C", 1: "D", 0: "F"}
    
    # Determine general skill tier of candidate
    skill_tier = random.choice(["S", "A", "B", "C"])
    
    for idx, boss in enumerate(bosses):
        base_val = grade_points[skill_tier]
        # Introduce slight variance per pull
        variance = random.choice([-1, 0, 0, 1]) if base_val > 1 else random.choice([0, 1])
        grade_val = max(0, min(5, base_val + variance))
        grade = reverse_points[grade_val]
        
        # Calculate other metrics
        dps = random.randint(120000, 180000) if chosen_class != "Priest" else random.randint(110000, 140000)
        avoidable_dmg = random.randint(20000, 80000) if grade_val >= 3 else random.randint(90000, 200000)
        panic_defensive = random.choice([True, True, True, False]) if grade_val >= 3 else random.choice([True, False, False])
        
        history.append({
            "pull_id": idx + 1,
            "boss_name": boss,
            "grade": grade,
            "dps": dps,
            "avoidable_damage": avoidable_dmg,
            "defensive_used_in_panic": panic_defensive
        })
        
    avg_grade_val = round(sum(grade_points[h["grade"]] for h in history) / len(history))
    overall_grade = reverse_points[avg_grade_val]
    
    # Calculate panic rate
    panic_opportunities = len(history)
    panic_successes = sum(1 for h in history if h["defensive_used_in_panic"])
    panic_rate = int((panic_successes / panic_opportunities) * 100)
    
    # Calculate prep score
    prep_score = random.randint(85, 100)
    
    # Compile focus tips
    focus_tips = []
    if overall_grade in ("S", "A"):
        focus_tips.append("Highly reliable mechanical play. Excellent candidate for mythic progression roster.")
        focus_tips.append("Defensive cooldown triggers align correctly with high-damage transition phases.")
    elif overall_grade == "B":
        focus_tips.append("Solid general performance. Occasional mistakes on late-phase movement mechanics.")
        focus_tips.append("Consumable prep is excellent, but panic-button defensive response has room to improve.")
    else:
        focus_tips.append("Rotational output is acceptable, but mechanical survival is inconsistent.")
        focus_tips.append("Frequent avoidable hits from ground-effect and traveling projectile mechanics.")
        
    return {
        "candidate": {
            "name": character_name,
            "realm": realm,
            "region": region.upper(),
            "class": chosen_class,
            "spec": chosen_spec,
            "item_level": random.randint(620, 630)
        },
        "overall_grade": overall_grade,
        "average_dps": int(sum(h["dps"] for h in history) / len(history)),
        "panic_defensive_rate": panic_rate,
        "preparation_score": prep_score,
        "history": history,
        "focus_tips": focus_tips
    }

def run_recruitment_audit(character_name: str, realm: str, region: str) -> str:
    """
    Spawns an audit job and stores it.
    """
    job_id = str(uuid.uuid4())
    # Create the report card
    report_card = get_candidate_report_card(character_name, realm, region)
    
    RECRUIT_JOBS[job_id] = {
        "job_id": job_id,
        "status": "completed",
        "result": report_card
    }
    return job_id

def get_recruitment_job(job_id: str) -> dict | None:
    return RECRUIT_JOBS.get(job_id)
