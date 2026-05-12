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


ENCOUNTER_ID = 3176
ENCOUNTER_NAME = "Imperator Averzian"


VOID_RUPTURE = {
    "name": "Void Rupture",
    "severity": "Critical",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "ground_effect",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": (
        "The remaining add will explode in a 12yd range and several beams "
        "will shoot out from the claimed space for a short time."
    ),
    "recommendation": (
        "Review movement pathing and avoid the impact zones."
    ),
    "wcl_type": "damage_taken",
}


VOID_FALL = {
    "name": "Void Fall",
    "severity": "Critical",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "ground_effect",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": (
        "Knockback followed by AOE circles on the ground that you need to dodge."
    ),
    "recommendation": (
        "Review movement pathing and avoid the impact zones."
    ),
    "wcl_type": "damage_taken",
}


OBLIVIONS_WRATH = {
    "name": "Oblivion's Wrath",
    "severity": "Warning",
    "avoidable": True,
    "category": "Movement",
    "failure_type": "dodge_missles",
    "counts_as_failure": True,
    "max_reasonable_hits": 4,
    "score_per_hit": 20,
    "applies_to": ALL_ROLES,
    "note": (
        "Several void beam spears shoot outward from Averzian, dealing damage "
        "and knocking players back."
    ),
    "recommendation": "Review movement pathing and avoid missiles.",
    "wcl_type": "damage_taken",
}


SHADOWS_ADVANCE = {
    "name": "Shadow's Advance",
    "severity": "Critical",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "ground_effect",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "A purple void zone spawns adds after exploding.",
    "recommendation": "Do not be in or near the void zones when they first appear.",
    "wcl_type": "damage_taken",
}


SHADOW_PHALANX = {
    "name": "Shadow Phalanx",
    "severity": "Critical",
    "avoidable": True,
    "category": "Movement",
    "failure_type": "dodge_oneshot",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "note": "The boss orders his army to march down a lane. Avoid touching these adds.",
    "recommendation": "Review movement pathing and avoid adds.",
    "wcl_type": "damage_taken",
}

BLACK_MIASMA = {
    "name": "Black Miasma",
    "severity": "Warning",
    "avoidable": True,
    "category": "Decurse",
    "failure_type": "decurse",
    "counts_as_failure": True,
    "max_reasonable_hits": 4,
    "score_per_hit": 20,
    "applies_to": ALL_ROLES,
    "note": "Multiple players are afflicted with Black Miasma.",
    "recommendation": "Decurse these players.",
    "wcl_type": "damage_taken",
}

DARK_BARRAGE = {
    "name": "Dark Barrage",
    "severity": "Major",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "ground_effect",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 60,
    "applies_to": ALL_ROLES,
    "note": (
        "Adds will hurl dark energy at several players."
    ),
    "recommendation": (
        "Review movement pathing and avoid the impact zones."
    ),
    "wcl_type": "damage_taken",
}

GNASHING_VOID = {
    "name": "Gnashing Void",
    "severity": "Info",
    "avoidable": True,
    "category": "Add Management",
    "failure_type": "kill_adds",
    "counts_as_failure": True,
    "max_reasonable_hits": 15,
    "score_per_hit": 1,
    "applies_to": ALL_ROLES,
    "note": (
        "Adds apply stacking shadow damage dot."
    ),
    "recommendation": (
        "Eliminate the adds faster."
    ),
    "wcl_type": "damage_taken",
}

AVOIDABLE_DAMAGE = {
    # Void Rupture
    **mechanic_aliases(
        [1261249, 1279890],
        VOID_RUPTURE,
    ),

    # Void Fall
    **mechanic_aliases(
        [1269160, 1258883],
        VOID_FALL,
    ),

    # Oblivion's Wrath
    **mechanic_aliases(
        [1260718],
        OBLIVIONS_WRATH,
    ),

    # Shadow's Advance
    **mechanic_aliases(
        [1253691],
        SHADOWS_ADVANCE,
    ),

    # Shadow Phalanx
    **mechanic_aliases(
        [1284786],
        SHADOW_PHALANX,
    ),
    # Black Miasma
    **mechanic_aliases(
        [1275059],
        BLACK_MIASMA,
    ),
    # Dark Barrage
    **mechanic_aliases(
        [1274846],
        DARK_BARRAGE,
    ),
    # Gnashing Void
    **mechanic_aliases(
        [1255683],
        GNASHING_VOID,
    ),
}