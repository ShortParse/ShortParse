# shortparse/data/cooldowns/evoker/shared.py

COOLDOWNS = {
    363916: {
        "name": "Obsidian Scales",
        "class": "EVOKER",
        "category": "personal_defensive",
        "notes": "Increases armor and reduces magic damage.",
        "cooldown_seconds": 150,

        "weight": "medium",

    },
    374251: {
        "name": "Renewing Blaze",
        "class": "EVOKER",
        "category": "personal_defensive",
        "notes": "Heals back damage taken over time.",
        "cooldown_seconds": 90,

        "weight": "medium",

    },
    374227: {
        "name": "Zephyr",
        "class": "EVOKER",
        "category": "raid_defensive",
        "notes": "Reduces AOE damage taken for the party.",
        "cooldown_seconds": 120,

        "weight": "high",

    },
    390386: {
        "name": "Fury of the Aspects",
        "class": "EVOKER",
        "category": "raid_utility",
        "notes": "Raid-wide haste increase.",
        "cooldown_seconds": 300,

        "weight": "high",

    },
    374968: {
        "name": "Time Spiral",
        "class": "EVOKER",
        "category": "raid_movement",
        "notes": "Allows party members to cast their class movement spell without CD.",
        "cooldown_seconds": 120,

        "weight": "high",

    },
}
