ROLE_GROUPS = {
    "tanks": "Tank",
    "healers": "Healer",
    "dps": "DPS",
}


def normalize_player_name(name: str) -> str:
    return (name or "").strip()


def safe_total(entry: dict) -> int:
    return int(entry.get("total") or 0)


def unwrap_table(table_data: dict) -> dict:
    if not isinstance(table_data, dict):
        return {}

    if "data" in table_data and isinstance(table_data["data"], dict):
        return table_data["data"]

    return table_data


def index_table_by_name(table_data: dict) -> dict:
    table_data = unwrap_table(table_data)

    if not table_data:
        return {}

    entries = table_data.get("entries", [])

    return {
        normalize_player_name(entry.get("name", "")): entry
        for entry in entries
        if normalize_player_name(entry.get("name", ""))
    }


def extract_spec(player: dict) -> str:
    specs = player.get("specs") or []

    if not specs:
        return "Unknown"

    return specs[0].get("spec", "Unknown")


def extract_item_level(player: dict) -> int:
    return int(
        player.get("maxItemLevel")
        or player.get("minItemLevel")
        or 0
    )


def find_role_groups(obj: dict) -> dict:
    """
    Warcraft Logs may wrap playerDetails in extra layers.
    This recursively searches until it finds tanks/healers/dps.
    """
    if not isinstance(obj, dict):
        return {}

    if any(key in obj for key in ROLE_GROUPS):
        return obj

    for value in obj.values():
        if isinstance(value, dict):
            found = find_role_groups(value)
            if found:
                return found

    return {}


def extract_player_details(player_details: dict) -> dict:
    players = {}

    role_groups = find_role_groups(player_details)

    if not role_groups:
        return players

    for group_key, role_name in ROLE_GROUPS.items():
        for player in role_groups.get(group_key, []):
            name = normalize_player_name(player.get("name", ""))

            if not name:
                continue

            players[name] = {
                "name": name,
                "class": player.get("type", "Unknown"),
                "spec": extract_spec(player),
                "role": role_name,
                "item_level": extract_item_level(player),
                "damage_done": 0,
                "healing_done": 0,
                "damage_taken": 0,
                "deaths": 0,
            }

    return players


def build_roster_from_fight_data(fight_data: dict) -> list[dict]:
    players = extract_player_details(fight_data.get("playerDetails", {}))

    damage_done = index_table_by_name(fight_data.get("damageDone", {}))
    healing = index_table_by_name(fight_data.get("healing", {}))
    damage_taken = index_table_by_name(fight_data.get("damageTaken", {}))
    deaths = index_table_by_name(fight_data.get("deaths", {}))

    all_names = set(players.keys())

    roster = []

    for name in sorted(all_names):
        player = players.get(
            name,
            {
                "name": name,
                "class": "Unknown",
                "spec": "Unknown",
                "role": "Unknown",
                "item_level": 0,
                "damage_done": 0,
                "healing_done": 0,
                "damage_taken": 0,
                "deaths": 0,
            },
        )

        player["damage_done"] = safe_total(damage_done.get(name, {}))
        player["healing_done"] = safe_total(healing.get(name, {}))
        player["damage_taken"] = safe_total(damage_taken.get(name, {}))

        death_entry = deaths.get(name, {})
        player["deaths"] = int(
            death_entry.get("total")
            or death_entry.get("deaths")
            or death_entry.get("count")
            or 0
        )

        roster.append(player)

    return roster