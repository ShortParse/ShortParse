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

FALLING = {
    "name": "Falling",
    "severity": "Critical",
    "avoidable": True,
    "category": "Gravity",
    "failure_type": "Watch that first step, it's a doozie.",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "note": (
        "The boss will attempt to pull players off the platform."
    ),
    "recommendation": (
        "Review movement pathing and avoid getting pulled off the platform."
    ),
    "wcl_type": "damage_taken",
}

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

AFTERSHOCK = {
    "name": "Aftershock",
    "severity": "Critical",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "Avoid ground effect",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 60,
    "applies_to": ALL_ROLES,
    "note": (
        "An expanding ring explodes after each Shadowclaw Slam."
    ),
    "recommendation": (
        "Check your positioning and move into a safe zone once a layer of ring explodes."
    ),
    "wcl_type": "damage_taken",
}

DARK_GOO = {
    "name": "Dark Goo",
    "severity": "Warning",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "Avoid ground effect",
    "counts_as_failure": True,
    "max_reasonable_hits": 4,
    "score_per_hit": 20,
    "applies_to": ALL_ROLES,
    "note": (
        "When the adds die, they begin to explode."
    ),
    "recommendation": (
        "Avoid standing in the explosive circle from the adds."
    ),
    "wcl_type": "damage_taken",
}

PARASITE_EXPULSION = {
    "name": "Parasite Expulsion",
    "severity": "Critical",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "Avoid ground effect",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": (
        "The boss will frequently spray globs of dark ichor across the battlefield."
    ),
    "recommendation": (
        "Avoid being in the explosive circle when they land."
    ),
    "wcl_type": "damage_taken",
}

BLISTERBURST = {
    "name": "Blistburst",
    "severity": "Warning",
    "avoidable": True,
    "category": "Add Management",
    "failure_type": "Touched by adds",
    "counts_as_failure": True,
    "max_reasonable_hits": 10,
    "score_per_hit": 10,
    "applies_to": ALL_ROLES,
    "note": (
        "Players targeted by adds will take damage while the adds are alive and in close proximity."
    ),
    "recommendation": (
        "Kill the adds faster."
    ),
    "wcl_type": "damage_taken",
}

AVOIDABLE_DAMAGE = {
    # Falling
    **mechanic_aliases(
        [3],
        FALLING,
    ),
    # Shadowclaw Slam
    **mechanic_aliases(
        [1272328, 1241808, 1281954, 1281906, 1272329, 1241807],
        SHADOWCLAW_SLAM,
    ),
    # Void Breath
    **mechanic_aliases(
        [1257607, 1259923, 1259921],
        VOID_BREATH,
    ),
    # Overpowering Pulse
    **mechanic_aliases(
        [1244419],
        OVERPOWERING_PULSE,
    ),
    # Aftershock
    **mechanic_aliases(
        [1276584, 1276828, 1276583, 1276829, 1276824, 1276581, 1276588, 1276830, 1276832, 1276812, 1276811, 1276833, 1276834, 1276813, 1276835, 1276817],
        AFTERSHOCK,
    ),
    # Dark Goo
    **mechanic_aliases(
        [1243270],
        DARK_GOO,
    ),
    # Parasite Expulsion
    **mechanic_aliases(
        [1275558, 1275556],
        PARASITE_EXPULSION,
    ),
    # Blisterburst
    **mechanic_aliases(
        [1259186, 1269302],
        BLISTERBURST,
    ),
}