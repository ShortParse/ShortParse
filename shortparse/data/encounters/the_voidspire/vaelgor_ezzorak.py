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

TAIL_LASH = {
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

IMPALE = {
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
}