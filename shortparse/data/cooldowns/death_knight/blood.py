# shortparse/data/cooldowns/death_knight/blood.py

COOLDOWNS = {
    55233: {
        "name": "Vampiric Blood",
        "class": "DEATH_KNIGHT",
        "specs": ['Blood'],
        "category": "tank_defensive",
        "notes": "Increases max health and healing received.",
        "cooldown_seconds": 90,

        "weight": "high",

    },
    49028: {
        "name": "Dancing Rune Weapon",
        "class": "DEATH_KNIGHT",
        "specs": ['Blood'],
        "category": "tank_defensive",
        "notes": "Increases parry chance and duplicates attacks.",
        "cooldown_seconds": 120,

        "weight": "high",

    },
    108199: {
        "name": "Gorefiend's Grasp",
        "class": "DEATH_KNIGHT",
        "specs": ['Blood'],
        "category": "raid_utility",
        "notes": "Pulls all enemies within 15 yards to the target location.",
        "cooldown_seconds": 60,

        "weight": "medium",

    },
    383269: {
        "name": "Abomination Limb",
        "class": "DEATH_KNIGHT",
        "specs": ['Blood'],
        "category": "personal_defensive",
        "notes": "Pulls enemies and grants Bone Shield charges.",
        "cooldown_seconds": 120,

        "weight": "medium",

    },
}
