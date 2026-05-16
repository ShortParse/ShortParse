from shortparse.data.encounters.types import Mechanic

from shortparse.data.encounters.constants import (
    ALL_ROLES,
    NON_TANK_ROLES,
    DPS_ONLY,
    HEALER_ONLY,
    TANK_ONLY,
)

from shortparse.data.encounters.mechanic_helper import (
    mechanic_aliases,
)


ENCOUNTER_ID = 3178
ENCOUNTER_NAME = "Vaelgor & Ezzorak"

TAIL_LASH: Mechanic = {
    "name": "Tail Lash",
    "severity": "Major",
    "avoidable": True,
    "category": "Positioning",
    "failure_type": "bad_position",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "note": (
        "Vaelgor knocks away players within a 35 yard rear cone."
    ),
    "recommendation": (
        "Review movement pathing and avoid standing behind Vaelgor."
    ),
    "wcl_type": "damage_taken",
}

IMPALE: Mechanic = {
    "name": "Impale",
    "severity": "Major",
    "avoidable": True,
    "category": "Positioning",
    "failure_type": "bad_position",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "note": (
        "Ezzorak slams targets within a 35 yard rear cone."
    ),
    "recommendation": (
        "Review movement pathing and avoid standing behind Ezzorak."
    ),
    "wcl_type": "damage_taken",
}

VAELWING: Mechanic = {
    "name": "Vaelwing",
    "severity": "Major",
    "avoidable": True,
    "category": "Boss Threat",
    "failure_type": "boss_threat",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 100,
    "applies_to": NON_TANK_ROLES,
    "note": (
        "Vaelgor buffets his primary target."
    ),
    "recommendation": (
        "Avoid taking threat from the tank."
    ),
    "wcl_type": "damage_taken",
}

RAKFANG: Mechanic = {
    "name": "Rakfang",
    "severity": "Major",
    "avoidable": True,
    "category": "Boss Threat",
    "failure_type": "boss_threat",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 100,
    "applies_to": NON_TANK_ROLES,
    "note": (
        "Ezzorak strikes his primary target."
    ),
    "recommendation": (
        "Avoid taking threat from the tank."
    ),
    "wcl_type": "damage_taken",
}

NULLSCATTER: Mechanic = {
    "name": "Nullscatter",
    "severity": "Critical",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "ground_effect",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": (
        "Nullzone's first tether snap releases a cascade of cosmic hail."
    ),
    "recommendation": (
        "Review movement pathing and avoid the impact zones."
    ),
    "wcl_type": "damage_taken",
}

MIDNIGHT_FLAMES: Mechanic = {
    "name": "Midnight Flames",
    "severity": "Critical",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "ground_effect",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "note": (
        "Upon reaching 100 energy, Vaelgor and Ezzorak fly as one."
    ),
    "recommendation": (
        "Review movement pathing and stay in the safe-zone bubble."
    ),
    "wcl_type": "damage_taken",
}

GLOOMFIELD: Mechanic = {
    "name": "Gloomfield",
    "severity": "Major",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "ground_effect",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 60,
    "applies_to": ALL_ROLES,
    "note": (
        "Galactic emptiness engulfs a massive location in darkness."
    ),
    "recommendation": (
        "Review movement pathing and avoid the impact zones."
    ),
    "wcl_type": "damage_taken",
}

GLOOM: Mechanic = {
    "name": "Gloom",
    "severity": "Info",
    "avoidable": True,
    "category": "Required Soak",
    "failure_type": "required_soak",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "spell_ids": [1245500],
    "note": (
        "Ezzorak ejects a moving mass of pure darkness in a frontal direction."
    ),
    "recommendation": (
        "Minimum of 5 players must soak this orb (On higher difficulties rotate soaks)."
    ),
    "wcl_type": "damage_taken",
}

AVOIDABLE_DAMAGE = {
    # Tail Lash
    **mechanic_aliases(
        [1264467],
        TAIL_LASH,
    ),
    # Impale
    **mechanic_aliases(
        [1265152],
        IMPALE,
    ),
    # Vaelwing
    **mechanic_aliases(
        [1265139],
        VAELWING,
    ),
    # Rakfang
    **mechanic_aliases(
        [1245652, 1245647],
        RAKFANG,
    ),
    # Nullscatter
    **mechanic_aliases(
        [1266570],
        NULLSCATTER,
    ),
    # Midnight Flames
    **mechanic_aliases(
        [1249748],
        MIDNIGHT_FLAMES,
    ),
    # Gloomfield
    **mechanic_aliases(
        [1245421],
        MIDNIGHT_FLAMES,
    ),

    # Gloom
    **mechanic_aliases(
        [1245500],
        GLOOM,
    ),
}