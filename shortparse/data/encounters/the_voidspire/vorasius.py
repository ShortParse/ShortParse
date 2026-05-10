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
    "category": "Frontal",
    "failure_type": "Hit by one-shot mechanic",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "note": (
        "The boss sweeps a deadly beam slowly across the room raid-wide."
    ),
    "recommendation": (
        "Ensure you break the walls to create egress, and then avoid getting touched by the beam."
    ),
    "wcl_type": "damage_taken",
}

OVERPOWERING_PULSE = {
    "name": "Overpowering Pulse",
    "severity": "Critical",
    "avoidable": True,
    "category": "Tank Positioning",
    "failure_type": "Tank out of melee range",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,

    # Responsibility belongs to the tank.
    "applies_to": TANK_ONLY,

    "note": (
        "Vorasius deals lethal raid-wide damage if no player "
        "is within melee range."
    ),

    "recommendation": (
        "At least one tank must remain in melee range "
        "at all times."
    ),

    "wcl_type": "damage_taken",
}

OVERPOWERING_PULSE = {
    "name": "Overpowering Pulse",
    "severity": "Critical",
    "avoidable": True,
    "category": "Tank Positioning",
    "failure_type": "Tank out of melee range",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,

    # Responsibility belongs to the tank.
    "applies_to": TANK_ONLY,

    "note": (
        "Vorasius deals lethal raid-wide damage if no player "
        "is within melee range."
    ),

    "recommendation": (
        "At least one tank must remain in melee range "
        "at all times."
    ),

    "wcl_type": "damage_taken",
}

AVOIDABLE_DAMAGE = {
    # Shadowclaw Slam
    **mechanic_aliases(
        [1241808, 1272328, 1281906, 1281954],
        SHADOWCLAW_SLAM,
    ),
    # Void Breath
    **mechanic_aliases(
        [1257607],
        VOID_BREATH,
    ),
    # Overpowering Pulse
    **mechanic_aliases(
        [1244419],
        OVERPOWERING_PULSE,
    )
}