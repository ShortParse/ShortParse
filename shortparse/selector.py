from collections import defaultdict


RAID_BOSSES = {
    "The Voidspire": {
        "Imperator Averzian",
        "Vorasius",
        "Fallen-King Salhadaar",
        "Vaelgor & Ezzorak",
        "Lightblinded Vanguard",
        "Crown of the Cosmos",
    },
    "The Dreamrift": {
        "Chimaerus",
    },
    "March on Quel'Danas": {
        "Belo'ren, Child of Al'ar",
        "Midnight Falls",
    },
}


def normalize_name(name: str) -> str:
    return " ".join((name or "").lower().split())


BOSS_TO_RAID = {
    normalize_name(boss_name): raid_name
    for raid_name, boss_names in RAID_BOSSES.items()
    for boss_name in boss_names
}


def get_raid_name_for_fight(fight: dict) -> str | None:
    boss_name = normalize_name(fight.get("name", ""))
    return BOSS_TO_RAID.get(boss_name)


def is_supported_raid_boss(fight: dict) -> bool:
    if fight.get("inProgress"):
        return False

    if not fight.get("encounterID"):
        return False

    if fight.get("bossPercentage") is None:
        return False

    if fight.get("fightPercentage") is None:
        return False

    return get_raid_name_for_fight(fight) is not None


def get_duration_seconds(fight: dict) -> int:
    return int((fight.get("endTime", 0) - fight.get("startTime", 0)) / 1000)


def get_progress_score(fight: dict) -> tuple:
    """
    Higher score wins.

    Uses Warcraft Logs' own fightPercentage and phase fields instead of
    guessing from boss HP or duration.

    lastPhaseAsAbsoluteIndex:
      Higher = later encounter phase.

    fightPercentage:
      Lower = deeper actual fight progression.
    """

    absolute_phase = fight.get("lastPhaseAsAbsoluteIndex")

    if absolute_phase is None:
        absolute_phase = 0

    fight_percentage = fight.get("fightPercentage")

    if fight_percentage is None:
        progress = 0.0
    else:
        progress = 100.0 - fight_percentage

    duration = get_duration_seconds(fight)

    return (
        absolute_phase,
        progress,
        duration,
    )


def select_best_boss_encounters(fights: list[dict]) -> dict[str, list[dict]]:
    grouped_by_raid_and_boss = defaultdict(lambda: defaultdict(list))

    for fight in fights:
        if not is_supported_raid_boss(fight):
            continue

        raid_name = get_raid_name_for_fight(fight)
        boss_key = (
            fight.get("encounterID") or normalize_name(fight.get("name", "")),
            fight.get("difficulty") or 0,
        )

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
                selected = max(
                    boss_fights,
                    key=get_progress_score,
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