# shortparse/data/cooldowns/priest/shadow.py

COOLDOWNS = {
    47585: {
        "name": "Dispersion",
        "class": "PRIEST",
        "specs": ['Shadow'],
        "category": "personal_defensive",
        "notes": "Reduces all damage taken by 75% and heals.",
        "cooldown_seconds": 120,

        "weight": "medium",

    },
    15286: {
        "name": "Vampiric Embrace",
        "class": "PRIEST",
        "specs": ['Shadow'],
        "category": "raid_utility",
        "notes": "Converts single-target shadow damage to raid healing.",
        "cooldown_seconds": 120,

        "weight": "high",

    },
}
