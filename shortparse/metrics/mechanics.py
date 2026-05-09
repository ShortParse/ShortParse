from shortparse.data.encounters.registry import get_avoidable_damage


def calculate_mechanics(
    roster: list[dict],
    events: list[dict],
    encounter_id: int,
) -> dict:

    mechanics = get_avoidable_damage(encounter_id)

    player_lookup = {
        player["actor_id"]: player["name"]
        for player in roster
    }

    player_mechanics = {}
    raid_mechanics = {}

    for event in events:
        if event.get("type") != "damage":
            continue

        actor_id = event.get("targetID")
        player_name = player_lookup.get(actor_id)

        if not player_name:
            continue

        spell_id = event.get("abilityGameID")
        mechanic = mechanics.get(spell_id)

        if not mechanic:
            continue

        mechanic_name = mechanic["name"]
        damage = int(event.get("amount") or 0)

        if player_name not in player_mechanics:
            player_mechanics[player_name] = {}

        if mechanic_name not in player_mechanics[player_name]:
            player_mechanics[player_name][mechanic_name] = {
                "hits": 0,
                "damage": 0,
            }

        player_mechanics[player_name][mechanic_name]["hits"] += 1
        player_mechanics[player_name][mechanic_name]["damage"] += damage

        if mechanic_name not in raid_mechanics:
            raid_mechanics[mechanic_name] = {
                "hits": 0,
                "damage": 0,
                "players_hit": set(),
                "worst_player": None,
                "worst_hits": 0,
            }

        raid_entry = raid_mechanics[mechanic_name]

        raid_entry["hits"] += 1
        raid_entry["damage"] += damage
        raid_entry["players_hit"].add(player_name)

    for mechanic_name, raid_entry in raid_mechanics.items():
        worst_player = None
        worst_hits = 0

        for player_name, player_data in player_mechanics.items():
            mechanic_data = player_data.get(mechanic_name)

            if not mechanic_data:
                continue

            hits = mechanic_data["hits"]

            if hits > worst_hits:
                worst_hits = hits
                worst_player = player_name

        raid_entry["worst_player"] = worst_player
        raid_entry["worst_hits"] = worst_hits
        raid_entry["players_hit"] = sorted(raid_entry["players_hit"])

    return {
        "player_mechanics": player_mechanics,
        "raid_mechanics": raid_mechanics,
    }