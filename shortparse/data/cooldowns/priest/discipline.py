# shortparse/data/cooldowns/priest/discipline.py

COOLDOWNS = {
    33206: {
        "name": "Pain Suppression",
        "class": "PRIEST",
        "specs": ['Discipline'],
        "category": "external_defensive",
        "notes": "Reduces target damage taken by 40%.",
        "cooldown_seconds": 180,
        "weight": "high",
    },
    62618: {
        "name": "Power Word: Barrier",
        "class": "PRIEST",
        "specs": ['Discipline'],
        "category": "raid_defensive",
        "notes": "Raid dome reducing damage taken by 25%.",
        "cooldown_seconds": 180,
        "weight": "high",
    },
    421453: {
        "name": "Ultimate Penitence",
        "class": "PRIEST",
        "specs": ['Discipline'],
        "category": "raid_defensive",
        "notes": "Fires a rapid flurry of Penance bolts while floating.",
        "cooldown_seconds": 240,
        "optional": True,
        "weight": "high",
    },
}
