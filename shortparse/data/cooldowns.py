# data/cooldowns.py

RAID_COOLDOWNS = {
    # Death Knight
    51052: {
        "name": "Anti-Magic Zone",
        "class": "DEATHKNIGHT",
        "category": "raid_defensive",
        "notes": "Raid magic damage reduction zone.",
        "cooldown_seconds": 120,
    },

    # Demon Hunter
    196718: {
        "name": "Netherwalk",
        "class": "DEMONHUNTER",
        "category": "personal_defensive",
        "notes": "Personal immunity-style defensive.",
        "cooldown_seconds": 180,
    },
    198589: {
        "name": "Blur",
        "class": "DEMONHUNTER",
        "category": "personal_defensive",
        "notes": "Personal defensive.",
        "cooldown_seconds": 60,
    },
    263648: {
        "name": "Soul Barrier",
        "class": "DEMONHUNTER",
        "category": "personal_defensive",
        "notes": "Vengeance defensive absorb.",
        "cooldown_seconds": 20,
    },
    212084: {
        "name": "Fel Devastation",
        "class": "DEMONHUNTER",
        "category": "tank_defensive",
        "notes": "Vengeance defensive/healing cooldown.",
        "cooldown_seconds": 40,
    },
    187827: {
        "name": "Metamorphosis",
        "class": "DEMONHUNTER",
        "category": "tank_defensive",
        "notes": "Vengeance major tank defensive.",
        "cooldown_seconds": 120,
    },

    # Druid
    740: {
        "name": "Tranquility",
        "class": "DRUID",
        "category": "raid_healing",
        "notes": "Major raid healing cooldown.",
        "cooldown_seconds": 180,
    },
    102342: {
        "name": "Ironbark",
        "class": "DRUID",
        "category": "external_defensive",
        "notes": "External defensive for one player.",
        "cooldown_seconds": 90,
    },
    77761: {
        "name": "Stampeding Roar",
        "class": "DRUID",
        "category": "raid_movement",
        "notes": "Raid movement cooldown.",
        "cooldown_seconds": 120,
    },

    # Evoker
    363534: {
        "name": "Rewind",
        "class": "EVOKER",
        "category": "raid_healing",
        "notes": "Major raid healing recovery cooldown.",
        "cooldown_seconds": 240,
    },
    374227: {
        "name": "Zephyr",
        "class": "EVOKER",
        "category": "raid_defensive",
        "notes": "Raid AoE damage reduction / movement utility.",
        "cooldown_seconds": 120,
    },
    374968: {
        "name": "Time Spiral",
        "class": "EVOKER",
        "category": "raid_movement",
        "notes": "Raid mobility utility.",
        "cooldown_seconds": 120,
    },
    370537: {
        "name": "Stasis",
        "class": "EVOKER",
        "category": "healing_utility",
        "notes": "Preservation stored healing setup.",
        "cooldown_seconds": 90,
    },

    # Hunter
    186265: {
        "name": "Aspect of the Turtle",
        "class": "HUNTER",
        "category": "personal_defensive",
        "notes": "Personal immunity-style defensive.",
        "cooldown_seconds": 180,
    },
    109304: {
        "name": "Exhilaration",
        "class": "HUNTER",
        "category": "personal_healing",
        "notes": "Personal self-heal.",
        "cooldown_seconds": 120,
    },

    # Mage
    45438: {
        "name": "Ice Block",
        "class": "MAGE",
        "category": "personal_immunity",
        "notes": "Personal immunity.",
        "cooldown_seconds": 240,
    },
    414658: {
        "name": "Mass Barrier",
        "class": "MAGE",
        "category": "raid_defensive",
        "notes": "Group shield cooldown.",
        "cooldown_seconds": 120,
    },
    414660: {
        "name": "Mass Invisibility",
        "class": "MAGE",
        "category": "raid_utility",
        "notes": "Group utility cooldown.",
        "cooldown_seconds": 300,
    },

    # Monk
    115310: {
        "name": "Revival",
        "class": "MONK",
        "category": "raid_healing",
        "notes": "Major instant raid healing cooldown.",
        "cooldown_seconds": 180,
    },
    116849: {
        "name": "Life Cocoon",
        "class": "MONK",
        "category": "external_defensive",
        "notes": "External absorb/defensive.",
        "cooldown_seconds": 120,
    },
    122278: {
        "name": "Dampen Harm",
        "class": "MONK",
        "category": "personal_defensive",
        "notes": "Personal defensive.",
        "cooldown_seconds": 120,
    },
    122783: {
        "name": "Diffuse Magic",
        "class": "MONK",
        "category": "personal_defensive",
        "notes": "Personal magic defensive.",
        "cooldown_seconds": 90,
    },

    # Paladin
    31821: {
        "name": "Aura Mastery",
        "class": "PALADIN",
        "category": "raid_defensive",
        "notes": "Major raid defensive cooldown.",
        "cooldown_seconds": 180,
    },
    6940: {
        "name": "Blessing of Sacrifice",
        "class": "PALADIN",
        "category": "external_defensive",
        "notes": "External damage transfer cooldown.",
        "cooldown_seconds": 120,
    },
    633: {
        "name": "Lay on Hands",
        "class": "PALADIN",
        "category": "emergency_healing",
        "notes": "Emergency single-target heal.",
        "cooldown_seconds": 600,
    },
    31850: {
        "name": "Ardent Defender",
        "class": "PALADIN",
        "category": "tank_defensive",
        "notes": "Protection Paladin major defensive.",
        "cooldown_seconds": 120,
    },
    86659: {
        "name": "Guardian of Ancient Kings",
        "class": "PALADIN",
        "category": "tank_defensive",
        "notes": "Protection Paladin major defensive.",
        "cooldown_seconds": 300,
    },

    # Priest
    62618: {
        "name": "Power Word: Barrier",
        "class": "PRIEST",
        "category": "raid_defensive",
        "notes": "Major raid damage reduction barrier.",
        "cooldown_seconds": 180,
    },
    64843: {
        "name": "Divine Hymn",
        "class": "PRIEST",
        "category": "raid_healing",
        "notes": "Major raid healing cooldown.",
        "cooldown_seconds": 180,
    },
    33206: {
        "name": "Pain Suppression",
        "class": "PRIEST",
        "category": "external_defensive",
        "notes": "External defensive cooldown.",
        "cooldown_seconds": 180,
    },
    47788: {
        "name": "Guardian Spirit",
        "class": "PRIEST",
        "category": "external_defensive",
        "notes": "External life-saving cooldown.",
        "cooldown_seconds": 180,
    },
    15286: {
        "name": "Vampiric Embrace",
        "class": "PRIEST",
        "category": "raid_healing",
        "notes": "Shadow raid healing utility.",
        "cooldown_seconds": 120,
    },

    # Rogue
    31224: {
        "name": "Cloak of Shadows",
        "class": "ROGUE",
        "category": "personal_immunity",
        "notes": "Personal magic immunity/cleanse.",
        "cooldown_seconds": 120,
    },
    5277: {
        "name": "Evasion",
        "class": "ROGUE",
        "category": "personal_defensive",
        "notes": "Personal defensive.",
        "cooldown_seconds": 120,
    },
    1966: {
        "name": "Feint",
        "class": "ROGUE",
        "category": "personal_defensive",
        "notes": "Frequent personal AoE defensive.",
        "cooldown_seconds": 15,
    },

    # Shaman
    98008: {
        "name": "Spirit Link Totem",
        "class": "SHAMAN",
        "specs": ["Restoration"],
        "category": "raid_defensive",
        "notes": "Major raid health redistribution / defensive cooldown.",
        "cooldown_seconds": 180,
    },
    108280: {
        "name": "Healing Tide Totem",
        "class": "SHAMAN",
        "category": "raid_healing",
        "notes": "Major raid healing cooldown.",
        "cooldown_seconds": 180,
    },
    198103: {
        "name": "Earth Elemental",
        "class": "SHAMAN",
        "category": "personal_utility",
        "notes": "Defensive/utility summon.",
        "cooldown_seconds": 300,
    },
    108271: {
        "name": "Astral Shift",
        "class": "SHAMAN",
        "category": "personal_defensive",
        "notes": "Personal defensive.",
        "cooldown_seconds": 90,
    },
    192077: {
        "name": "Wind Rush Totem",
        "class": "SHAMAN",
        "category": "raid_movement",
        "notes": "Raid movement cooldown.",
        "cooldown_seconds": 120,
    },

    # Warlock
    104773: {
        "name": "Unending Resolve",
        "class": "WARLOCK",
        "category": "personal_defensive",
        "notes": "Personal defensive.",
        "cooldown_seconds": 180,
    },
    108416: {
        "name": "Dark Pact",
        "class": "WARLOCK",
        "category": "personal_defensive",
        "notes": "Personal absorb defensive.",
        "cooldown_seconds": 60,
    },
    20707: {
        "name": "Soulstone",
        "class": "WARLOCK",
        "category": "battle_res",
        "notes": "Combat resurrection utility.",
        "cooldown_seconds": 600,
    },

    # Warrior
    97462: {
        "name": "Rallying Cry",
        "class": "WARRIOR",
        "category": "raid_defensive",
        "notes": "Major raid max-health defensive cooldown.",
        "cooldown_seconds": 180,
    },
    871: {
        "name": "Shield Wall",
        "class": "WARRIOR",
        "category": "tank_defensive",
        "notes": "Protection Warrior major defensive.",
        "cooldown_seconds": 240,
    },
    12975: {
        "name": "Last Stand",
        "class": "WARRIOR",
        "category": "tank_defensive",
        "notes": "Protection Warrior major health cooldown.",
        "cooldown_seconds": 180,
    },
    118038: {
        "name": "Die by the Sword",
        "class": "WARRIOR",
        "category": "personal_defensive",
        "notes": "DPS Warrior personal defensive.",
        "cooldown_seconds": 120,
    },
}


RAID_COOLDOWN_IDS = set(RAID_COOLDOWNS.keys())


def get_cooldown(spell_id: int) -> dict | None:
    return RAID_COOLDOWNS.get(spell_id)


def is_raid_cooldown(spell_id: int) -> bool:
    return spell_id in RAID_COOLDOWN_IDS


def normalize_class_name(class_name: str) -> str:
    return (
        str(class_name or "")
        .replace(" ", "")
        .replace("_", "")
        .upper()
    )


def get_cooldowns_for_class(
    class_name: str,
    spec_name: str | None = None,
) -> dict:
    normalized_class = normalize_class_name(class_name)
    normalized_spec = normalize_class_name(spec_name or "")

    results = {}

    for spell_id, cooldown in RAID_COOLDOWNS.items():
        cooldown_class = normalize_class_name(
            cooldown.get("class")
        )

        if cooldown_class != normalized_class:
            continue

        cooldown_specs = cooldown.get("specs")

        if cooldown_specs:
            normalized_specs = {
                normalize_class_name(spec)
                for spec in cooldown_specs
            }

            if normalized_spec not in normalized_specs:
                continue

        results[spell_id] = cooldown

    return results