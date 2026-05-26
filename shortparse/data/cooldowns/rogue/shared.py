# shortparse/data/cooldowns/rogue/shared.py

COOLDOWNS = {
    31224: {
        "name": "Cloak of Shadows",
        "class": "ROGUE",
        "category": "personal_immunity",
        "notes": "Magic damage immunity and debuff purge.",
        "cooldown_seconds": 120,

        "weight": "medium",

    },
    5277: {
        "name": "Evasion",
        "class": "ROGUE",
        "category": "personal_defensive",
        "notes": "Increases dodge chance by 100%.",
        "cooldown_seconds": 120,

        "weight": "medium",

    },
    1966: {
        "name": "Feint",
        "class": "ROGUE",
        "category": "personal_defensive",
        "notes": "Reduces AOE damage taken.",
        "cooldown_seconds": 15,

        "weight": "low",

    },
    1856: {
        "name": "Vanish",
        "class": "ROGUE",
        "category": "personal_defensive",
        "notes": "Enters stealth instantly, dropping all combat threat.",
        "cooldown_seconds": 120,

        "weight": "low",

    },
}
