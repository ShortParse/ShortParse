# metrics/cooldowns.py

RAID_COOLDOWNS = {
    # Death Knight
    51052: {
        "name": "Anti-Magic Zone",
        "class": "DEATHKNIGHT",
        "category": "raid_defensive",
        "notes": "Raid magic damage reduction zone.",
    },

    # Demon Hunter
    196718: {
        "name": "Netherwalk",
        "class": "DEMONHUNTER",
        "category": "personal_defensive",
        "notes": "Personal immunity-style defensive.",
    },
    198589: {
        "name": "Blur",
        "class": "DEMONHUNTER",
        "category": "personal_defensive",
        "notes": "Personal defensive.",
    },
    263648: {
        "name": "Soul Barrier",
        "class": "DEMONHUNTER",
        "category": "personal_defensive",
        "notes": "Vengeance defensive absorb.",
    },
    212084: {
        "name": "Fel Devastation",
        "class": "DEMONHUNTER",
        "category": "tank_defensive",
        "notes": "Vengeance defensive/healing cooldown.",
    },
    187827: {
        "name": "Metamorphosis",
        "class": "DEMONHUNTER",
        "category": "tank_defensive",
        "notes": "Vengeance major tank defensive.",
    },

    # Druid
    740: {
        "name": "Tranquility",
        "class": "DRUID",
        "category": "raid_healing",
        "notes": "Major raid healing cooldown.",
    },
    102342: {
        "name": "Ironbark",
        "class": "DRUID",
        "category": "external_defensive",
        "notes": "External defensive for one player.",
    },
    77761: {
        "name": "Stampeding Roar",
        "class": "DRUID",
        "category": "raid_movement",
        "notes": "Raid movement cooldown.",
    },

    # Evoker
    363534: {
        "name": "Rewind",
        "class": "EVOKER",
        "category": "raid_healing",
        "notes": "Major raid healing recovery cooldown.",
    },
    374227: {
        "name": "Zephyr",
        "class": "EVOKER",
        "category": "raid_defensive",
        "notes": "Raid AoE damage reduction / movement utility.",
    },
    374968: {
        "name": "Time Spiral",
        "class": "EVOKER",
        "category": "raid_movement",
        "notes": "Raid mobility utility.",
    },
    370537: {
        "name": "Stasis",
        "class": "EVOKER",
        "category": "healing_utility",
        "notes": "Preservation stored healing setup.",
    },

    # Hunter
    186265: {
        "name": "Aspect of the Turtle",
        "class": "HUNTER",
        "category": "personal_defensive",
        "notes": "Personal immunity-style defensive.",
    },
    109304: {
        "name": "Exhilaration",
        "class": "HUNTER",
        "category": "personal_healing",
        "notes": "Personal self-heal.",
    },

    # Mage
    45438: {
        "name": "Ice Block",
        "class": "MAGE",
        "category": "personal_immunity",
        "notes": "Personal immunity.",
    },
    414658: {
        "name": "Mass Barrier",
        "class": "MAGE",
        "category": "raid_defensive",
        "notes": "Group shield cooldown.",
    },
    414660: {
        "name": "Mass Invisibility",
        "class": "MAGE",
        "category": "raid_utility",
        "notes": "Group utility cooldown.",
    },

    # Monk
    115310: {
        "name": "Revival",
        "class": "MONK",
        "category": "raid_healing",
        "notes": "Major instant raid healing cooldown.",
    },
    116849: {
        "name": "Life Cocoon",
        "class": "MONK",
        "category": "external_defensive",
        "notes": "External absorb/defensive.",
    },
    122278: {
        "name": "Dampen Harm",
        "class": "MONK",
        "category": "personal_defensive",
        "notes": "Personal defensive.",
    },
    122783: {
        "name": "Diffuse Magic",
        "class": "MONK",
        "category": "personal_defensive",
        "notes": "Personal magic defensive.",
    },

    # Paladin
    31821: {
        "name": "Aura Mastery",
        "class": "PALADIN",
        "category": "raid_defensive",
        "notes": "Major raid defensive cooldown.",
    },
    6940: {
        "name": "Blessing of Sacrifice",
        "class": "PALADIN",
        "category": "external_defensive",
        "notes": "External damage transfer cooldown.",
    },
    633: {
        "name": "Lay on Hands",
        "class": "PALADIN",
        "category": "emergency_healing",
        "notes": "Emergency single-target heal.",
    },
    31850: {
        "name": "Ardent Defender",
        "class": "PALADIN",
        "category": "tank_defensive",
        "notes": "Protection Paladin major defensive.",
    },
    86659: {
        "name": "Guardian of Ancient Kings",
        "class": "PALADIN",
        "category": "tank_defensive",
        "notes": "Protection Paladin major defensive.",
    },

    # Priest
    62618: {
        "name": "Power Word: Barrier",
        "class": "PRIEST",
        "category": "raid_defensive",
        "notes": "Major raid damage reduction barrier.",
    },
    64843: {
        "name": "Divine Hymn",
        "class": "PRIEST",
        "category": "raid_healing",
        "notes": "Major raid healing cooldown.",
    },
    33206: {
        "name": "Pain Suppression",
        "class": "PRIEST",
        "category": "external_defensive",
        "notes": "External defensive cooldown.",
    },
    47788: {
        "name": "Guardian Spirit",
        "class": "PRIEST",
        "category": "external_defensive",
        "notes": "External life-saving cooldown.",
    },
    15286: {
        "name": "Vampiric Embrace",
        "class": "PRIEST",
        "category": "raid_healing",
        "notes": "Shadow raid healing utility.",
    },

    # Rogue
    31224: {
        "name": "Cloak of Shadows",
        "class": "ROGUE",
        "category": "personal_immunity",
        "notes": "Personal magic immunity/cleanse.",
    },
    5277: {
        "name": "Evasion",
        "class": "ROGUE",
        "category": "personal_defensive",
        "notes": "Personal defensive.",
    },
    1966: {
        "name": "Feint",
        "class": "ROGUE",
        "category": "personal_defensive",
        "notes": "Frequent personal AoE defensive.",
    },

    # Shaman
    98008: {
        "name": "Spirit Link Totem",
        "class": "SHAMAN",
        "category": "raid_defensive",
        "notes": "Major raid health redistribution / defensive cooldown.",
    },
    108280: {
        "name": "Healing Tide Totem",
        "class": "SHAMAN",
        "category": "raid_healing",
        "notes": "Major raid healing cooldown.",
    },
    198103: {
        "name": "Earth Elemental",
        "class": "SHAMAN",
        "category": "personal_utility",
        "notes": "Defensive/utility summon.",
    },
    108271: {
        "name": "Astral Shift",
        "class": "SHAMAN",
        "category": "personal_defensive",
        "notes": "Personal defensive.",
    },
    192077: {
        "name": "Wind Rush Totem",
        "class": "SHAMAN",
        "category": "raid_movement",
        "notes": "Raid movement cooldown.",
    },

    # Warlock
    104773: {
        "name": "Unending Resolve",
        "class": "WARLOCK",
        "category": "personal_defensive",
        "notes": "Personal defensive.",
    },
    108416: {
        "name": "Dark Pact",
        "class": "WARLOCK",
        "category": "personal_defensive",
        "notes": "Personal absorb defensive.",
    },
    20707: {
        "name": "Soulstone",
        "class": "WARLOCK",
        "category": "battle_res",
        "notes": "Combat resurrection utility.",
    },

    # Warrior
    97462: {
        "name": "Rallying Cry",
        "class": "WARRIOR",
        "category": "raid_defensive",
        "notes": "Major raid max-health defensive cooldown.",
    },
    871: {
        "name": "Shield Wall",
        "class": "WARRIOR",
        "category": "tank_defensive",
        "notes": "Protection Warrior major defensive.",
    },
    12975: {
        "name": "Last Stand",
        "class": "WARRIOR",
        "category": "tank_defensive",
        "notes": "Protection Warrior major health cooldown.",
    },
    118038: {
        "name": "Die by the Sword",
        "class": "WARRIOR",
        "category": "personal_defensive",
        "notes": "DPS Warrior personal defensive.",
    },
}


RAID_COOLDOWN_IDS = set(RAID_COOLDOWNS.keys())


def get_cooldown(spell_id: int) -> dict | None:
    return RAID_COOLDOWNS.get(spell_id)


def is_raid_cooldown(spell_id: int) -> bool:
    return spell_id in RAID_COOLDOWN_IDS