# shortparse/metrics/activity.py

ACTIVE_EVENT_TYPES = {
    "cast",
    "begincast",
}


def calculate_active_time(
    actor_id: int,
    events: list[dict],
    fight_duration_seconds: float,
    fight_start_time: int,
) -> dict:

    player_timestamps = []

    for event in events:
        if event.get("sourceID") != actor_id:
            continue

        if event.get("type") not in ACTIVE_EVENT_TYPES:
            continue

        timestamp = event.get("timestamp")

        if timestamp is None:
            continue

        player_timestamps.append(timestamp)

    if not player_timestamps:
        return {
            "active_time_pct": 0.0,
            "inactive_seconds": round(fight_duration_seconds, 2),
            "gaps": [],
            "gaps_count": 0,
            "gaps_total_seconds": 0.0
        }

    player_timestamps.sort()

    ACTIVE_WINDOW_MS = 4000
    GAP_THRESHOLD_MS = 5000  # 5 seconds of inactivity

    active_ms = 0
    gaps = []

    previous = player_timestamps[0]

    for timestamp in player_timestamps[1:]:
        delta = timestamp - previous

        active_ms += min(delta, ACTIVE_WINDOW_MS)

        if delta >= GAP_THRESHOLD_MS:
            gaps.append({
                "start_seconds": round((previous - fight_start_time) / 1000, 2),
                "duration_seconds": round(delta / 1000, 2)
            })

        previous = timestamp

    active_seconds = active_ms / 1000

    active_pct = (
        active_seconds / fight_duration_seconds
    ) * 100

    active_pct = min(active_pct, 100.0)

    inactive_seconds = max(
        0,
        fight_duration_seconds - active_seconds,
    )

    return {
        "active_time_pct": round(active_pct, 2),
        "inactive_seconds": round(inactive_seconds, 2),
        "gaps": gaps,
        "gaps_count": len(gaps),
        "gaps_total_seconds": round(sum(g["duration_seconds"] for g in gaps), 2)
    }