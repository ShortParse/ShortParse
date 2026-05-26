# shortparse/data/cooldowns/paladin/shared.py

COOLDOWNS = {
    642: {
        "name": "Divine Shield",
        "class": "PALADIN",
        "category": "personal_immunity",
        "notes": "Provides complete damage and spell immunity.",
        "cooldown_seconds": 300,

        "weight": "high",

    },
    102242: {
        "name": "Blessing of Sacrifice",
        "class": "PALADIN",
        "category": "external_defensive",
        "notes": "Transfers damage from an ally to the Paladin.",
        "cooldown_seconds": 120,

        "weight": "high",

    },
    1022: {
        "name": "Blessing of Protection",
        "class": "PALADIN",
        "category": "external_defensive",
        "notes": "Immunity to physical damage and bleed effects.",
        "cooldown_seconds": 300,

        "weight": "high",

    },
    633: {
        "name": "Lay on Hands",
        "class": "PALADIN",
        "category": "external_defensive",
        "notes": "Heals an ally for the Paladin's maximum health.",
        "cooldown_seconds": 600,

        "weight": "high",

    },
}
