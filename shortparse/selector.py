from collections import defaultdict


RAID_NAMES = {
    "the voidspire": "The Voidspire",
    "the dreamrift": "The Dreamrift",
    "march on quel'danas": "March on Quel'Danas",
    "march on queldanas": "March on Quel'Danas",
}


def guess_raid_name(fight: dict) -> str:
    """
    Temporary POC logic.

    Warcraft Logs fight objects reliably give us boss names and encounter IDs.
    Raid/zone grouping may need a second gameData/zones lookup later.

    For now, we group known Midnight raid fights by name matching.
    Unknown boss fights go into 'Unknown Raid'.
    """

    name = (fight.get("name") or "").lower()

    # POC placeholder:
    # We will replace this with encounterID -> raid mapping once we pull zones.
    for raid_key, raid_name in RAID_NAMES.items():
        if raid_key in name:
            return raid_name

    return "Unknown Raid"


def is_boss_fight(fight: dict) -> bool:
    return bool(fight.get("encounterID")) and fight.get("bossPercentage") is not None


def select_best_boss_encounters(fights: list[dict]) -> dict[str, list[dict]]:
    grouped_by_raid_and_boss = defaultdict(lambda: defaultdict(list))

    for fight in fights:
        if fight.get("inProgress"):
            continue

        if not is_boss_fight(fight):
            continue

        raid_name = guess_raid_name(fight)
        boss_key = fight.get("encounterID") or fight.get("name")

        grouped_by_raid_and_boss[raid_name][boss_key].append(fight)

    selected_by_raid = defaultdict(list)

    for raid_name, bosses in grouped_by_raid_and_boss.items():
        for boss_key, boss_fights in bosses.items():
            kills = [fight for fight in boss_fights if fight.get("kill")]

            if kills:
                selected = sorted(
                    kills,
                    key=lambda fight: fight.get("endTime", 0),
                )[-1]
            else:
                selected = min(
                    boss_fights,
                    key=lambda fight: fight.get("bossPercentage", 100.0),
                )

            selected_by_raid[raid_name].append(selected)

    for raid_name in selected_by_raid:
        selected_by_raid[raid_name].sort(
            key=lambda fight: (
                fight.get("encounterID") or 0,
                fight.get("startTime") or 0,
            )
        )

    return dict(selected_by_raid)