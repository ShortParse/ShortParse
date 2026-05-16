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


ENCOUNTER_ID = 3182
ENCOUNTER_NAME = "Belo'ren, Child of Al'ar"

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