# shortparse/data/cooldowns/warrior/shared.py

COOLDOWNS = {
    23920: {
        "name": "Spell Reflection",
        "class": "WARRIOR",
        "category": "personal_defensive",
        "notes": "Reflects magic spells and reduces magic damage.",
        "cooldown_seconds": 25,

        "weight": "low",

    },
    97462: {
        "name": "Rallying Cry",
        "class": "WARRIOR",
        "category": "raid_defensive",
        "notes": "Increases max health for the entire party.",
        "cooldown_seconds": 180,

        "weight": "high",

    },
    3411: {
        "name": "Intervene",
        "class": "WARRIOR",
        "category": "external_defensive",
        "notes": "Intercepts next physical/melee attack on targeted ally.",
        "cooldown_seconds": 30,

        "weight": "low",

    },
}
