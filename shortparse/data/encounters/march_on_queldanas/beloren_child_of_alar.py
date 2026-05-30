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


from .zone_id import ZONE_ID

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
    "mrt": True,
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
    "mrt": True,
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
    "mrt": True,
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
    "mrt": True,
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
    "mrt": True,
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
    "mrt": True,
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
    "mrt": True,
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
    "mrt": True,
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
    "mrt": True,
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
    "mrt": False,
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
    "mrt": True,
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
    "mrt": True,
}

BURNING_HEART: Mechanic = {
    "name": "Burning Heart",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 75,
    "applies_to": ALL_ROLES,
    "spell_ids": [1264650],
    "note": "Player stood in Burning Heart ground effect or failed debuff mechanics.",
    "recommendation": "Move out of the Burning Heart effect immediately.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

VOIDLIGHT_CONVERGENCE: Mechanic = {
    "name": "Voidlight Convergence",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 70,
    "applies_to": ALL_ROLES,
    "spell_ids": [1241932],
    "note": "Player hit by Voidlight Convergence beam or projectile.",
    "recommendation": "Dodge the incoming Voidlight Convergence beams.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

LIGHT_FLAMES: Mechanic = {
    "name": "Light Flames",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 75,
    "applies_to": ALL_ROLES,
    "spell_ids": [1242803],
    "note": "Player stood in Light Flames ground patch.",
    "recommendation": "Quickly step out of Light Flames pools.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

VOID_FLAMES: Mechanic = {
    "name": "Void Flames",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 75,
    "applies_to": ALL_ROLES,
    "spell_ids": [1242815],
    "note": "Player stood in Void Flames ground patch.",
    "recommendation": "Quickly step out of Void Flames pools.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

LIGHT_ECHO: Mechanic = {
    "name": "Light Echo",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 70,
    "applies_to": ALL_ROLES,
    "spell_ids": [1242991],
    "note": "Player was hit by a Light Echo explosion.",
    "recommendation": "Dodge the exploding Light Echo circles.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

VOID_ECHO: Mechanic = {
    "name": "Void Echo",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 70,
    "applies_to": ALL_ROLES,
    "spell_ids": [1242996],
    "note": "Player was hit by a Void Echo explosion.",
    "recommendation": "Dodge the exploding Void Echo circles.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

LIGHT_EDICT: Mechanic = {
    "name": "Light Edict",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "spell_ids": [1241646, 1265781],
    "note": "Player failed to manage Light Edict circle or ran into another player's Edict.",
    "recommendation": "Move away from other players when afflicted with Light Edict.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

VOID_EDICT: Mechanic = {
    "name": "Void Edict",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "spell_ids": [1241676, 1265793],
    "note": "Player failed to manage Void Edict circle or ran into another player's Edict.",
    "recommendation": "Move away from other players when afflicted with Void Edict.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

ASHEN_BENEDICTION: Mechanic = {
    "name": "Ashen Benediction",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 75,
    "applies_to": ALL_ROLES,
    "spell_ids": [1262573],
    "note": "Player took avoidable damage from Ashen Benediction.",
    "recommendation": "Dodge the Ashen Benediction projectiles and ground effects.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

LIGHT_BURN: Mechanic = {
    "name": "Light Burn",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 70,
    "applies_to": ALL_ROLES,
    "spell_ids": [1244348],
    "note": "Player suffered from Light Burn due to standing in avoidable Light hazards.",
    "recommendation": "Avoid taking avoidable Light damage to prevent Light Burn.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

VOID_BURN: Mechanic = {
    "name": "Void Burn",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 70,
    "applies_to": ALL_ROLES,
    "spell_ids": [1266404],
    "note": "Player suffered from Void Burn due to standing in avoidable Void hazards.",
    "recommendation": "Avoid taking avoidable Void damage to prevent Void Burn.",
    "wcl_type": "damage_taken",
    "mrt": True,
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
    **mechanic_aliases([1264650], BURNING_HEART),
    **mechanic_aliases([1241932], VOIDLIGHT_CONVERGENCE),
    **mechanic_aliases([1242803], LIGHT_FLAMES),
    **mechanic_aliases([1242815], VOID_FLAMES),
    **mechanic_aliases([1242991], LIGHT_ECHO),
    **mechanic_aliases([1242996], VOID_ECHO),
    **mechanic_aliases([1241646, 1265781], LIGHT_EDICT),
    **mechanic_aliases([1241676, 1265793], VOID_EDICT),
    **mechanic_aliases([1262573], ASHEN_BENEDICTION),
    **mechanic_aliases([1244348], LIGHT_BURN),
    **mechanic_aliases([1266404], VOID_BURN),
}