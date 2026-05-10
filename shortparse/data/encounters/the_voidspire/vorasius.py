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

ENCOUNTER_ID = 3177
ENCOUNTER_NAME = "Vorasius"

SHADOWCLAW_SLAM = {
    "name": "Shadowclaw Slam",
    "severity": "Critical",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "Repeated avoidable hits",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": NON_TANK_ROLES,
    "note": (
        "The boss slams the circles on the ground, this is a tank only mechanic."
    ),
    "recommendation": (
        "Review movement pathing and avoid standing in tank circle."
    ),
    "wcl_type": "damage_taken",
}

VOID_BREATH = {
    "name": "Void Breath",
    "severity": "Critical",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "Repeated avoidable hits",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": NON_TANK_ROLES,
    "note": (
        "The boss slams the circles on the ground, this is a tank only mechanic."
    ),
    "recommendation": (
        "Review movement pathing and avoid standing in tank circle."
    ),
    "wcl_type": "damage_taken",
}

AVOIDABLE_DAMAGE = {
    # Shadowclaw Slam
    **mechanic_aliases(
        [1241808, 1272328, 1281906, 1281954],
        SHADOWCLAW_SLAM,
    ),
}