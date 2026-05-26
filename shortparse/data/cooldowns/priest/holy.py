# shortparse/data/cooldowns/priest/holy.py

COOLDOWNS = {
    47788: {
        "name": "Guardian Spirit",
        "class": "PRIEST",
        "specs": ['Holy'],
        "category": "external_defensive",
        "notes": "Increases target healing and prevents death.",
        "cooldown_seconds": 180,

        "weight": "high",

    },
    64843: {
        "name": "Divine Hymn",
        "class": "PRIEST",
        "specs": ['Holy'],
        "category": "raid_defensive",
        "notes": "Channeled raid-wide healing and healing-buff.",
        "cooldown_seconds": 180,

        "weight": "high",

    },
    64901: {
        "name": "Symbol of Hope",
        "class": "PRIEST",
        "specs": ['Holy'],
        "category": "raid_utility",
        "notes": "Raid-wide mana return and cooldown reduction.",
        "cooldown_seconds": 180,

        "weight": "high",

    },
}
