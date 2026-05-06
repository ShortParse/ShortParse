def safe_get_total(entry: dict) -> int:
    return int(entry.get("total") or 0)


def normalize_player_name(name: str) -> str:
    return (name or "").strip()


def index_table_by_name(table_data: dict) -> dict:
    """
    Warcraft Logs table JSON usually contains an 'entries' list.
    Each entry often has 'name' and 'total'.
    """
    indexed = {}

    if not table_data:
        return indexed

    entries = table_data.get("entries", [])

    for entry in entries:
        name = normalize_player_name(entry.get("name", ""))

        if not name:
            continue

        indexed[name] = entry

    return indexed


def extract_player_details(player_details: dict) -> dict:
    """
    Build base roster from playerDetails.
    WCL's playerDetails shape can vary slightly, so this is defensive.
    """
    players = {}

    if not player_details:
        return players

    categories = player_details.get("playerDetails", [])

    for category in categories:
        for player in category.get("players", []):
            name = normalize_player_name(player.get("name", ""))

            if not name:
                continue

            players[name] = {
                "name": name,
                "class": player.get("type", "Unknown"),
                "spec": player.get("spec", "Unknown"),
                "role": player.get("role", "Unknown"),
                "item_level": player.get("itemLevel") or player.get("minItemLevel") or 0,
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
    all_names.update(damage_done.keys())
    all_names.update(healing.keys())
    all_names.update(damage_taken.keys())
    all_names.update(deaths.keys())

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

        player["damage_done"] = safe_get_total(damage_done.get(name, {}))
        player["healing_done"] = safe_get_total(healing.get(name, {}))
        player["damage_taken"] = safe_get_total(damage_taken.get(name, {}))

        death_entry = deaths.get(name, {})
        player["deaths"] = int(death_entry.get("total") or death_entry.get("deaths") or 0)

        roster.append(player)

    return roster