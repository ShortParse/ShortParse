import json
from pathlib import Path
from shortparse.database import SessionLocal
from shortparse.db_models import Job

def calculate_trend_slope(y_values: list[int]) -> float:
    """
    Calculates the linear slope of a sequence of numerical grades.
    """
    n = len(y_values)
    if n < 3:
        return 0.0  # Need at least 3 points to determine a trend
    
    x_values = list(range(n))
    mean_x = sum(x_values) / n
    mean_y = sum(y_values) / n
    
    numerator = sum((x_values[i] - mean_x) * (y_values[i] - mean_y) for i in range(n))
    denominator = sum((x_values[i] - mean_x) ** 2 for i in range(n))
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator

def get_slump_tracker_analytics() -> dict:
    """
    Aggregates historical data across all successfully completed jobs
    to calculate skill trends and potential performance slumps.
    """
    db = SessionLocal()
    try:
        # Fetch completed jobs sorted chronologically by creation date
        completed_jobs = db.query(Job).filter(Job.status == "completed").order_by(Job.created_at.asc()).all()
        
        player_histories = {}
        grade_points = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
        
        # Parse scorecard history from result files
        for job in completed_jobs:
            if not job.result_path:
                continue
                
            path = Path(job.result_path)
            if not path.exists():
                continue
                
            try:
                with open(path, "r", encoding="utf-8") as f:
                    result_data = json.load(f)
                    
                fight_name = result_data.get("fight", {}).get("name", "Unknown Boss")
                end_time = result_data.get("fight", {}).get("end_time") or 0
                
                scorecard = result_data.get("scorecard", [])
                for entry in scorecard:
                    player_name = entry.get("player")
                    grade = entry.get("grade", "C")
                    dps = entry.get("dps", 0)
                    hps = entry.get("hps", 0)
                    avoidable_damage = entry.get("avoidable_damage", 0)
                    
                    if not player_name:
                        continue
                        
                    if player_name not in player_histories:
                        player_histories[player_name] = {
                            "name": player_name,
                            "class": entry.get("class") or entry.get("spec") or "Unknown",
                            "spec": entry.get("spec", "Unknown"),
                            "role": entry.get("role", "Unknown"),
                            "history": []
                        }
                        
                    player_histories[player_name]["history"].append({
                        "fight_name": fight_name,
                        "timestamp": end_time,
                        "grade": grade,
                        "grade_val": grade_points.get(grade, 2),
                        "dps": dps,
                        "hps": hps,
                        "avoidable_damage": avoidable_damage
                    })
            except Exception:
                # Silently skip malformed result files
                continue
                
        # Calculate trends for each player
        tracker_results = []
        for name, data in player_histories.items():
            # Sort player history chronologically
            data["history"].sort(key=lambda x: x["timestamp"])
            
            history_len = len(data["history"])
            y_values = [h["grade_val"] for h in data["history"]]
            
            # Calculate trend
            slope = calculate_trend_slope(y_values)
            
            # Classify trend status
            if slope < -0.15:
                trend = "down"
            elif slope > 0.15:
                trend = "up"
            else:
                trend = "stable"
                
            # Compile slump alerts and constructive focus advice
            alert_message = None
            focus_rec = None
            
            if trend == "down" and history_len >= 3:
                recent_avoidable = sum(h["avoidable_damage"] for h in data["history"][-3:]) / 3
                earlier_avoidable = sum(h["avoidable_damage"] for h in data["history"][:-3]) / max(1, history_len - 3)
                
                if recent_avoidable > earlier_avoidable * 1.25:
                    alert_message = f"Mechanical survival grade is in a slump due to rising avoidable damage."
                    focus_rec = "Focus on ground-effect positioning and review phase transition movement guides."
                else:
                    alert_message = f"Grade average has slumped over recent fights."
                    focus_rec = "Focus on rotation uptime, cooldown scheduling, and overall active time."
            elif trend == "up" and history_len >= 3:
                alert_message = "Mechanical consistency is steadily climbing!"
                focus_rec = "Excellent progression and mechanical consistency. Keep it up!"
            else:
                alert_message = "Consistent and stable performance."
                focus_rec = "Maintain current rotational reliability and positioning awareness."

            # Calculate average grade over their whole history
            avg_val = round(sum(y_values) / max(1, len(y_values)))
            reverse_points = {5: "S", 4: "A", 3: "B", 2: "C", 1: "D", 0: "F"}
            avg_grade = reverse_points.get(avg_val, "C")
            
            tracker_results.append({
                "name": name,
                "class": data["class"],
                "spec": data["spec"],
                "role": data["role"],
                "history": data["history"],
                "avg_grade": avg_grade,
                "trend": trend,
                "slope": round(slope, 3),
                "alert": alert_message,
                "focus_recommendation": focus_rec
            })
            
        # Sort results by name alphabetically
        tracker_results.sort(key=lambda x: x["name"])
        
        return {
            "status": "success",
            "players": tracker_results
        }
    finally:
        db.close()
