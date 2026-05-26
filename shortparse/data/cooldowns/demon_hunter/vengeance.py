# shortparse/data/cooldowns/demon_hunter/vengeance.py

COOLDOWNS = {
    187827: {
        "name": "Metamorphosis",
        "class": "DEMON_HUNTER",
        "specs": ['Vengeance'],
        "category": "tank_defensive",
        "notes": "Increases health and armor.",
        "cooldown_seconds": 240,

        "weight": "high",

    },
    204020: {
        "name": "Fiery Brand",
        "class": "DEMON_HUNTER",
        "specs": ['Vengeance'],
        "category": "tank_defensive",
        "notes": "Reduces target damage done to the player.",
        "cooldown_seconds": 60,

        "weight": "high",

    },
    202137: {
        "name": "Sigil of Silence",
        "class": "DEMON_HUNTER",
        "specs": ['Vengeance'],
        "category": "raid_utility",
        "notes": "Silences all enemies in the sigil's area.",
        "cooldown_seconds": 60,

        "weight": "medium",

    },
    202138: {
        "name": "Sigil of Chains",
        "class": "DEMON_HUNTER",
        "specs": ['Vengeance'],
        "category": "raid_utility",
        "notes": "Pulls all enemies to the center of the sigil and snares.",
        "cooldown_seconds": 90,

        "weight": "medium",

    },
}
