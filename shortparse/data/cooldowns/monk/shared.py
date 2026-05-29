# shortparse/data/cooldowns/monk/shared.py

COOLDOWNS = {
    115203: {
        "name": "Fortifying Brew",
        "class": "MONK",
        "category": "personal_defensive",
        "notes": "Increases health and reduces damage taken.",
        "cooldown_seconds": 360,
        "weight": "medium",
    },
    122783: {
        "name": "Diffuse Magic",
        "class": "MONK",
        "category": "personal_defensive",
        "notes": "Cleanses magic debuffs and reduces magic damage.",
        "cooldown_seconds": 90,
        "optional": True,
        "weight": "medium",
    },
    122278: {
        "name": "Dampen Harm",
        "class": "MONK",
        "category": "personal_defensive",
        "notes": "Reduces damage taken from large hits.",
        "cooldown_seconds": 120,
        "optional": True,
        "weight": "medium",
    },
    116844: {
        "name": "Ring of Peace",
        "class": "MONK",
        "category": "raid_utility",
        "notes": "Forms a ring pushing out enemies.",
        "cooldown_seconds": 45,
        "optional": True,
        "weight": "low",
    },
}
