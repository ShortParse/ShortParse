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


ENCOUNTER_ID = 3306
ENCOUNTER_NAME = "Chimaerus the Undreamt God"

# ============================================================
# Chimaerus the Undreamt God
# ============================================================

ALNDUST_UPHEAVAL: Mechanic = {
    "name": "Alndust Upheaval",
    "severity": "Critical",
    "avoidable": False,
    "category": "soak",
    "failure_type": "missed_soak",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "spell_ids": [1262305, 1246827],
    "note": (
        "Players must soak the tank impact to split damage and enter the Rift."
    ),
    "recommendation": (
        "Soak with your assigned group and avoid soaking consecutive sets."
    ),
    "wcl_type": "damage_taken",
}

DISSONANCE: Mechanic = {
    "name": "Dissonance",
    "severity": "Major",
    "avoidable": True,
    "category": "group_positioning",
    "failure_type": "positioning_failure",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 40,
    "applies_to": ALL_ROLES,
    "spell_ids": [1268666, 1267201],
    "note": (
        "Players damage allies in the opposing realm when positioned incorrectly."
    ),
    "recommendation": (
        "Stay grouped with your realm team and separated from the opposite realm."
    ),
    "wcl_type": "damage_taken",
}

RIFT_MADNESS: Mechanic = {
    "name": "Rift Madness",
    "severity": "Critical",
    "avoidable": True,
    "category": "coordination",
    "failure_type": "missed_assist",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 70,
    "applies_to": ALL_ROLES,
    "spell_ids": [1275637, 1264782],
    "note": (
        "Players afflicted with Rift Madness must be rescued via realm swap."
    ),
    "recommendation": (
        "Assigned players should quickly swap realms with afflicted targets."
    ),
    "wcl_type": "damage_taken",
}

FEARSOME_CRY: Mechanic = {
    "name": "Fearsome Cry",
    "severity": "Critical",
    "avoidable": True,
    "category": "interrupt",
    "failure_type": "missed_interrupt",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 70,
    "applies_to": ALL_ROLES,
    "spell_ids": [1265940, 1249017],
    "note": (
        "Fearsome Cry fears the raid and should always be interrupted."
    ),
    "recommendation": (
        "Interrupt Fearsome Cry immediately."
    ),
    "wcl_type": "damage_taken",
}

ESSENCE_BOLT: Mechanic = {
    "name": "Essence Bolt",
    "severity": "Minor",
    "avoidable": True,
    "category": "interrupt",
    "failure_type": "missed_interrupt",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 20,
    "applies_to": ALL_ROLES,
    "spell_ids": [1261997],
    "note": (
        "Essence Bolt is interruptible add damage."
    ),
    "recommendation": (
        "Interrupt Essence Bolt when possible."
    ),
    "wcl_type": "damage_taken",
}

CANNIBALIZED_ESSENCE: Mechanic = {
    "name": "Cannibalized Essence",
    "severity": "Critical",
    "avoidable": True,
    "category": "add_failure",
    "failure_type": "failed_add_control",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "spell_ids": [1280655],
    "note": (
        "Chimaerus consumed remaining Manifestations."
    ),
    "recommendation": (
        "Kill or control all Manifestations before Consume or Ravenous Dive."
    ),
    "wcl_type": "damage_taken",
}

CORRUPTED_DEVASTATION: Mechanic = {
    "name": "Corrupted Devastation",
    "severity": "Critical",
    "avoidable": True,
    "category": "beam",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 90,
    "applies_to": ALL_ROLES,
    "spell_ids": [1245486],
    "note": (
        "Massive sweeping corruption beam across the arena."
    ),
    "recommendation": (
        "Move out of the beam path immediately."
    ),
    "wcl_type": "damage_taken",
}

RENDING_TEAR: Mechanic = {
    "name": "Rending Tear",
    "severity": "Major",
    "avoidable": True,
    "category": "frontal",
    "failure_type": "frontal_hit",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 60,
    "applies_to": ALL_ROLES,
    "spell_ids": [1272726],
    "note": (
        "Heavy frontal cone attack with bleed and knockback."
    ),
    "recommendation": (
        "Stay out of the frontal cone."
    ),
    "wcl_type": "damage_taken",
}

ALNDUST_ESSENCE: Mechanic = {
    "name": "Alndust Essence",
    "severity": "Minor",
    "avoidable": True,
    "category": "ground_effect",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 3,
    "score_per_hit": 15,
    "applies_to": ALL_ROLES,
    "spell_ids": [1245919],
    "note": (
        "Damaging puddles left behind after manifestations lose their shields."
    ),
    "recommendation": (
        "Move out of Alndust Essence puddles."
    ),
    "wcl_type": "damage_taken",
}


AVOIDABLE_DAMAGE = {
    **mechanic_aliases([1262305, 1246827], ALNDUST_UPHEAVAL),
    **mechanic_aliases([1268666, 1267201], DISSONANCE),
    **mechanic_aliases([1275637, 1264782], RIFT_MADNESS),
    **mechanic_aliases([1265940, 1249017], FEARSOME_CRY),
    **mechanic_aliases([1261997], ESSENCE_BOLT),
    **mechanic_aliases([1280655], CANNIBALIZED_ESSENCE),
    **mechanic_aliases([1245486], CORRUPTED_DEVASTATION),
    **mechanic_aliases([1272726], RENDING_TEAR),
    **mechanic_aliases([1245919], ALNDUST_ESSENCE),
}