SPEC_ROLES = {
    # Death Knight
    ("DeathKnight", "Blood"): "Tank",
    ("DeathKnight", "Frost"): "DPS",
    ("DeathKnight", "Unholy"): "DPS",

    # Demon Hunter
    ("DemonHunter", "Havoc"): "DPS",
    ("DemonHunter", "Vengeance"): "Tank",

    # Druid
    ("Druid", "Balance"): "DPS",
    ("Druid", "Feral"): "DPS",
    ("Druid", "Guardian"): "Tank",
    ("Druid", "Restoration"): "Healer",

    # Evoker
    ("Evoker", "Devastation"): "DPS",
    ("Evoker", "Preservation"): "Healer",
    ("Evoker", "Augmentation"): "DPS",

    # Hunter
    ("Hunter", "BeastMastery"): "DPS",
    ("Hunter", "Marksmanship"): "DPS",
    ("Hunter", "Survival"): "DPS",

    # Mage
    ("Mage", "Arcane"): "DPS",
    ("Mage", "Fire"): "DPS",
    ("Mage", "Frost"): "DPS",

    # Monk
    ("Monk", "Brewmaster"): "Tank",
    ("Monk", "Mistweaver"): "Healer",
    ("Monk", "Windwalker"): "DPS",

    # Paladin
    ("Paladin", "Holy"): "Healer",
    ("Paladin", "Protection"): "Tank",
    ("Paladin", "Retribution"): "DPS",

    # Priest
    ("Priest", "Discipline"): "Healer",
    ("Priest", "Holy"): "Healer",
    ("Priest", "Shadow"): "DPS",

    # Rogue
    ("Rogue", "Assassination"): "DPS",
    ("Rogue", "Outlaw"): "DPS",
    ("Rogue", "Subtlety"): "DPS",

    # Shaman
    ("Shaman", "Elemental"): "DPS",
    ("Shaman", "Enhancement"): "DPS",
    ("Shaman", "Restoration"): "Healer",

    # Warlock
    ("Warlock", "Affliction"): "DPS",
    ("Warlock", "Demonology"): "DPS",
    ("Warlock", "Destruction"): "DPS",

    # Warrior
    ("Warrior", "Arms"): "DPS",
    ("Warrior", "Fury"): "DPS",
    ("Warrior", "Protection"): "Tank",
}


def normalize_name(value: str | None) -> str:
    return (
        str(value or "")
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
        .upper()
    )


def normalize_spec_key(
    class_name: str | None,
    spec_name: str | None,
) -> tuple[str, str]:
    return (
        normalize_name(class_name),
        normalize_name(spec_name),
    )


_NORMALIZED_SPEC_ROLES = {
    normalize_spec_key(class_name, spec_name): role
    for (class_name, spec_name), role in SPEC_ROLES.items()
}


def get_spec_role(
    class_name: str | None,
    spec_name: str | None,
) -> str:
    return _NORMALIZED_SPEC_ROLES.get(
        normalize_spec_key(class_name, spec_name),
        "Unknown",
    )


def is_tank(
    class_name: str | None,
    spec_name: str | None,
) -> bool:
    return get_spec_role(class_name, spec_name) == "Tank"


def is_healer(
    class_name: str | None,
    spec_name: str | None,
) -> bool:
    return get_spec_role(class_name, spec_name) == "Healer"


def is_dps(
    class_name: str | None,
    spec_name: str | None,
) -> bool:
    return get_spec_role(class_name, spec_name) == "DPS"