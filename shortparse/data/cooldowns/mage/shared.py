# shortparse/data/cooldowns/mage/shared.py

COOLDOWNS = {
    45438: {
        "name": "Ice Block",
        "class": "MAGE",
        "category": "personal_immunity",
        "notes": "Provides absolute damage and debuff immunity.",
        "cooldown_seconds": 240,

        "weight": "medium",

    },
    110959: {
        "name": "Greater Invisibility",
        "class": "MAGE",
        "category": "personal_defensive",
        "notes": "Reduces damage taken and drops threat.",
        "cooldown_seconds": 120,

        "weight": "low",

    },
    414658: {
        "name": "Mass Barrier",
        "class": "MAGE",
        "category": "raid_defensive",
        "notes": "Applies shields to the entire party.",
        "cooldown_seconds": 120,

        "weight": "medium",

    },
    80353: {
        "name": "Time Warp",
        "class": "MAGE",
        "category": "raid_utility",
        "notes": "Raid-wide haste increase.",
        "cooldown_seconds": 300,

        "weight": "high",

    },
    108920: {
        "name": "Alter Time",
        "class": "MAGE",
        "category": "personal_defensive",
        "notes": "Remembers health/position, returns after 10s or re-cast.",
        "cooldown_seconds": 60,

        "weight": "low",

    },
    55342: {
        "name": "Mirror Image",
        "class": "MAGE",
        "category": "personal_defensive",
        "notes": "Summons 3 images, reducing damage taken by 20%.",
        "cooldown_seconds": 120,

        "weight": "low",

    },
}
