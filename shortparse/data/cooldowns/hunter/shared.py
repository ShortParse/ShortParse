# shortparse/data/cooldowns/hunter/shared.py

COOLDOWNS = {
    186265: {
        "name": "Aspect of the Turtle",
        "class": "HUNTER",
        "category": "personal_immunity",
        "notes": "Deflects attacks and reduces damage taken.",
        "cooldown_seconds": 180,

        "weight": "high",

    },
    109304: {
        "name": "Exhilaration",
        "class": "HUNTER",
        "category": "personal_defensive",
        "notes": "Heals the hunter and pet instantly.",
        "cooldown_seconds": 120,

        "weight": "medium",

    },
    264735: {
        "name": "Survival of the Fittest",
        "class": "HUNTER",
        "category": "personal_defensive",
        "notes": "Command Pet defensive cooldown.",
        "cooldown_seconds": 180,

        "weight": "medium",

    },
    264667: {
        "name": "Primal Rage",
        "class": "HUNTER",
        "category": "raid_utility",
        "notes": "Raid-wide haste increase (Pet-based).",
        "cooldown_seconds": 300,

        "weight": "high",

    },
}
