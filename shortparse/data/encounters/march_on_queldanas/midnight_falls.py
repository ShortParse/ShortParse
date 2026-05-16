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


ENCOUNTER_ID = 3183
ENCOUNTER_NAME = "Midnight Falls"

VOID_RUPTURE: Mechanic = {
    "name": "Void Rupture",
    "severity": "Critical",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "Repeated avoidable hits",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": (
        "The remaining add will explode in a 12yd range and several beams "
        "will shoot out from the claimed space for a short time."
    ),
    "recommendation": (
        "Review movement pathing and avoid blue circles on the floor."
    ),
    "wcl_type": "damage_taken",
}


AVOIDABLE_DAMAGE = {
    # Void Rupture
    **mechanic_aliases(
        [1261249, 1279890],
        VOID_RUPTURE,
    ),
}









###############################
AVOIDABLE_DAMAGE = {
    1251649: {
        "name": "Disintegration",
        "severity": "Warning",
        "note": "Change me later.",
    },

    # Heaven's Glaives
    1254076: {
        "name": "Heaven's Glaives",
        "severity": "Critical",

        # Core classification
        "avoidable": True,
        "category": "Movement",
        "failure_type": "Repeated avoidable hits",

        # Scoring / filtering
        "counts_as_failure": True,
        "max_reasonable_hits": 1,
        "score_per_hit": 20,

        # Role logic
        "roles": ["DPS", "Healer", "Tank"],
        "tank_only": False,
        "healer_only": False,

        # Display / analysis
        "note": "Avoidable blade hits. Repeated hits usually indicate poor movement or bad positioning.",
        "recommendation": "Review movement pathing and avoid standing in blade travel lines.",

        # Optional future fields
        "wcl_type": "damage_taken",
        "spell_id": 1254076,
    },

    1279420: {
        "name": "Dark Quasar",
        "severity": "Critical",
        "note": "Change me later.",
    },
    1254646: {
        "name": "The Darkwell",
        "severity": "Critical",
        "note": "Change me later.",
    },
    1282034: {
        "name": "Into the darkwell",
        "severity": "Critical",
        "note": "Change me later.",
    },
    1250898: {
        "name": "Dark Archangel",
        "severity": "Critical",
        "note": "Change me later.",
    },
    1266388: {
        "name": "Dark Constellation",
        "severity": "Critical",
        "note": "Change me later.",
    },
    1266897: {
        "name": "Light Siphon",
        "severity": "Critical",
        "note": "Change me later.",
    },
}