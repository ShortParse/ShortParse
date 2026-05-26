# shortparse/data/cooldowns/druid/restoration.py

COOLDOWNS = {
    740: {
        "name": "Tranquility",
        "class": "DRUID",
        "specs": ['Restoration'],
        "category": "raid_defensive",
        "notes": "Raid-wide channeled healing cooldown.",
        "cooldown_seconds": 180,
    },
    102342: {
        "name": "Ironbark",
        "class": "DRUID",
        "specs": ['Restoration'],
        "category": "external_defensive",
        "notes": "External damage reduction on a party member.",
        "cooldown_seconds": 90,
    },
}
