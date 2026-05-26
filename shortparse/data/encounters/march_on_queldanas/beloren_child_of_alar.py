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

# ============================================================
# Belo'ren, Child of Al'ar
# ============================================================

LIGHT_DIVE: Mechanic = {
    "name": "Light Dive",
    "severity": "Critical",
    "avoidable": False,
    "category": "soak",
    "failure_type": "missed_soak",
    "counts_as_failure": False,
    "max_reasonable_hits": 1,
    "score_per_hit": 70,
    "applies_to": ALL_ROLES,
    "spell_ids": [1241291],
    "note": (
        "Light Dive must be soaked by players with matching color."
    ),
    "recommendation": (
        "Soak Light Dive with Light players and place puddles at room edges."
    ),
    "wcl_type": "damage_taken",
}

VOID_DIVE: Mechanic = {
    "name": "Void Dive",
    "severity": "Critical",
    "avoidable": False,
    "category": "soak",
    "failure_type": "missed_soak",
    "counts_as_failure": False,
    "max_reasonable_hits": 1,
    "score_per_hit": 70,
    "applies_to": ALL_ROLES,
    "spell_ids": [1241340],
    "note": (
        "Void Dive must be soaked by players with matching color."
    ),
    "recommendation": (
        "Soak Void Dive with Void players and place puddles at room edges."
    ),
    "wcl_type": "damage_taken",
}

LIGHT_ERUPTION: Mechanic = {
    "name": "Light Eruption",
    "severity": "Critical",
    "avoidable": True,
    "category": "interrupt",
    "failure_type": "missed_interrupt",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "spell_ids": [1243852, 1282416],
    "note": (
        "Light Eruption is lethal and must be interrupted by Light players."
    ),
    "recommendation": (
        "Assigned Light players must interrupt immediately."
    ),
    "wcl_type": "damage_taken",
}

VOID_ERUPTION: Mechanic = {
    "name": "Void Eruption",
    "severity": "Critical",
    "avoidable": True,
    "category": "interrupt",
    "failure_type": "missed_interrupt",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "spell_ids": [1243854, 1282415],
    "note": (
        "Void Eruption is lethal and must be interrupted by Void players."
    ),
    "recommendation": (
        "Assigned Void players must interrupt immediately."
    ),
    "wcl_type": "damage_taken",
}

LIGHT_QUILL: Mechanic = {
    "name": "Light Quill",
    "severity": "Major",
    "avoidable": True,
    "category": "line_soak",
    "failure_type": "failed_soak",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 50,
    "applies_to": ALL_ROLES,
    "spell_ids": [1242093],
    "note": (
        "Light Quill must be intercepted by matching-color players."
    ),
    "recommendation": (
        "Light players should intercept Light Quills safely."
    ),
    "wcl_type": "damage_taken",
}

VOID_QUILL: Mechanic = {
    "name": "Void Quill",
    "severity": "Major",
    "avoidable": True,
    "category": "line_soak",
    "failure_type": "failed_soak",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 50,
    "applies_to": ALL_ROLES,
    "spell_ids": [1242094],
    "note": (
        "Void Quill must be intercepted by matching-color players."
    ),
    "recommendation": (
        "Void players should intercept Void Quills safely."
    ),
    "wcl_type": "damage_taken",
}

VOIDLIGHT_RUPTURE: Mechanic = {
    "name": "Voidlight Rupture",
    "severity": "Critical",
    "avoidable": True,
    "category": "wrong_color",
    "failure_type": "incorrect_soak",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 90,
    "applies_to": ALL_ROLES,
    "spell_ids": [1243866],
    "note": (
        "Player contacted an orb of the wrong color."
    ),
    "recommendation": (
        "Only soak echoes matching your assigned color."
    ),
    "wcl_type": "damage_taken",
}

LIGHT_PATCH: Mechanic = {
    "name": "Light Patch",
    "severity": "Info",
    "avoidable": True,
    "category": "ground_effect",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 3,
    "score_per_hit": 15,
    "applies_to": ALL_ROLES,
    "spell_ids": [1241840],
    "note": (
        "Persistent Light puddle damage."
    ),
    "recommendation": (
        "Avoid standing in Light Patch."
    ),
    "wcl_type": "damage_taken",
}

VOID_PATCH: Mechanic = {
    "name": "Void Patch",
    "severity": "Info",
    "avoidable": True,
    "category": "ground_effect",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 3,
    "score_per_hit": 15,
    "applies_to": ALL_ROLES,
    "spell_ids": [1241841],
    "note": (
        "Persistent Void puddle damage."
    ),
    "recommendation": (
        "Avoid standing in Void Patch."
    ),
    "wcl_type": "damage_taken",
}

GUARDIANS_EDICT: Mechanic = {
    "name": "Guardian's Edict",
    "severity": "Critical",
    "avoidable": True,
    "category": "tank_mechanic",
    "failure_type": "failed_tank_soak",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": TANK_ONLY,
    "spell_ids": [1260826],
    "note": (
        "Guardian's Edict failed or hit incorrect players."
    ),
    "recommendation": (
        "Tanks must correctly soak matching color frontal cones."
    ),
    "wcl_type": "damage_taken",
}

REBIRTH: Mechanic = {
    "name": "Rebirth",
    "severity": "Critical",
    "avoidable": True,
    "category": "add_failure",
    "failure_type": "failed_add_kill",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "spell_ids": [1263412],
    "note": (
        "Ember egg respawned because it was not destroyed in time."
    ),
    "recommendation": (
        "Kill eggs immediately after embers die."
    ),
    "wcl_type": "damage_taken",
}

DEATH_DROP: Mechanic = {
    "name": "Death Drop",
    "severity": "Major",
    "avoidable": True,
    "category": "positioning",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 40,
    "applies_to": ALL_ROLES,
    "spell_ids": [1241333],
    "note": (
        "Players were too close to the impact zone during Death Drop."
    ),
    "recommendation": (
        "Move away from center before Death Drop lands."
    ),
    "wcl_type": "damage_taken",
}


AVOIDABLE_DAMAGE = {
    **mechanic_aliases([1241291], LIGHT_DIVE),
    **mechanic_aliases([1241340], VOID_DIVE),
    **mechanic_aliases([1243852, 1282416], LIGHT_ERUPTION),
    **mechanic_aliases([1243854, 1282415], VOID_ERUPTION),
    **mechanic_aliases([1242093], LIGHT_QUILL),
    **mechanic_aliases([1242094], VOID_QUILL),
    **mechanic_aliases([1243866], VOIDLIGHT_RUPTURE),
    **mechanic_aliases([1241840], LIGHT_PATCH),
    **mechanic_aliases([1241841], VOID_PATCH),
    **mechanic_aliases([1260826], GUARDIANS_EDICT),
    **mechanic_aliases([1263412], REBIRTH),
    **mechanic_aliases([1241333], DEATH_DROP),
}