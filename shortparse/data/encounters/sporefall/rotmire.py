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


ENCOUNTER_ID = 53159
ENCOUNTER_NAME = "Rotmire"


BURSTING_DOOM_SHROOM: Mechanic = {
    "name": "Bursting Doom Shroom",
    "severity": "Critical",
    "avoidable": True,
    "category": "swirl",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "note": "Player took damage from Bursting Doom Shroom. Extremely high damage one-shot mechanic.",
    "recommendation": "Avoid standing in Bursting Doom Shroom impact circles.",
    "wcl_type": "damage_taken",
}

PUTRID_FIST: Mechanic = {
    "name": "Putrid Fist",
    "severity": "Major",
    "avoidable": True,
    "category": "frontal",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 50,
    "applies_to": ALL_ROLES,
    "note": "Player took damage from Putrid Fist. Heavy avoidable physical slam.",
    "recommendation": "Step out of the frontal slam trajectory.",
    "wcl_type": "damage_taken",
}

POISON_BURST: Mechanic = {
    "name": "Poison Burst",
    "severity": "Warning",
    "avoidable": True,
    "category": "swirl",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 30,
    "applies_to": ALL_ROLES,
    "note": "Player took damage from Poison Burst impact.",
    "recommendation": "Dodge the incoming poison swirl zones.",
    "wcl_type": "damage_taken",
}

AWAKEN_FUNGI: Mechanic = {
    "name": "Awaken Fungi",
    "severity": "Warning",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 30,
    "applies_to": ALL_ROLES,
    "note": "Player took damage from Awaken Fungi spawn impacts.",
    "recommendation": "Step away from growing mushrooms before they spawn.",
    "wcl_type": "damage_taken",
}

FUNGAL_BLOOM: Mechanic = {
    "name": "Fungal Bloom",
    "severity": "Warning",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 30,
    "applies_to": ALL_ROLES,
    "note": "Player took damage from Fungal Bloom explosion.",
    "recommendation": "Step out of the expanding bloom ring.",
    "wcl_type": "damage_taken",
}

BURSTING_SHROOM: Mechanic = {
    "name": "Bursting Shroom",
    "severity": "Warning",
    "avoidable": True,
    "category": "swirl",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 30,
    "applies_to": ALL_ROLES,
    "note": "Player took damage from a Bursting Shroom explosion.",
    "recommendation": "Dodge the exploding shroom impact zones.",
    "wcl_type": "damage_taken",
}

FESTERING_VINES: Mechanic = {
    "name": "Festering Vines",
    "severity": "Warning",
    "avoidable": True,
    "category": "ground_effect",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 30,
    "applies_to": ALL_ROLES,
    "note": "Player stood in Festering Vines ground patch.",
    "recommendation": "Dodge the growing festering vine patches on the ground.",
    "wcl_type": "damage_taken",
}

WRITHING_VINES: Mechanic = {
    "name": "Writhing Vines",
    "severity": "Warning",
    "avoidable": True,
    "category": "ground_effect",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 30,
    "applies_to": ALL_ROLES,
    "note": "Player stood in Writhing Vines ground patch.",
    "recommendation": "Avoid walking into the writhing vine regions.",
    "wcl_type": "damage_taken",
}

ROTTEN_BOLT: Mechanic = {
    "name": "Rotten Bolt",
    "severity": "Warning",
    "avoidable": True,
    "category": "traveling_projectile",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 30,
    "applies_to": ALL_ROLES,
    "note": "Player hit by avoidable Rotten Bolt projectile.",
    "recommendation": "Dodge the flying Rotten Bolt projectiles.",
    "wcl_type": "damage_taken",
}

BURSTING_PUSTULES: Mechanic = {
    "name": "Bursting Pustules",
    "severity": "Warning",
    "avoidable": True,
    "category": "swirl",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 30,
    "applies_to": ALL_ROLES,
    "note": "Player hit by a bursting pustule impact zone.",
    "recommendation": "Avoid standing in the bursting pustule impact swirls.",
    "wcl_type": "damage_taken",
}

ROTTING_PUSTULES: Mechanic = {
    "name": "Rotting Pustules",
    "severity": "Warning",
    "avoidable": True,
    "category": "debuff_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 30,
    "applies_to": ALL_ROLES,
    "note": "Player stood in Rotting Pustules pool.",
    "recommendation": "Move out of the rotting green pools immediately.",
    "wcl_type": "damage_taken",
}

BLIGHTSHOT: Mechanic = {
    "name": "Blightshot",
    "severity": "Warning",
    "avoidable": True,
    "category": "traveling_projectile",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 30,
    "applies_to": ALL_ROLES,
    "note": "Player took damage from Blightshot projectile.",
    "recommendation": "Dodge incoming Blightshot missiles.",
    "wcl_type": "damage_taken",
}

SPOREFALL: Mechanic = {
    "name": "Sporefall",
    "severity": "Warning",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 30,
    "applies_to": ALL_ROLES,
    "note": "Player took damage from falling spore impact.",
    "recommendation": "Step away from target locations of falling spores.",
    "wcl_type": "damage_taken",
}


AVOIDABLE_DAMAGE = {
    **mechanic_aliases([1221901], AWAKEN_FUNGI),
    **mechanic_aliases([1221717], BLIGHTSHOT),
    **mechanic_aliases([1222495], BURSTING_DOOM_SHROOM),
    **mechanic_aliases([1222278], BURSTING_PUSTULES),
    **mechanic_aliases([1221965], BURSTING_SHROOM),
    **mechanic_aliases([1222088, 1222122], FESTERING_VINES),
    **mechanic_aliases([1221637], FUNGAL_BLOOM),
    **mechanic_aliases([1221714], POISON_BURST),
    **mechanic_aliases([1221781], PUTRID_FIST),
    **mechanic_aliases([1221970], ROTTEN_BOLT),
    **mechanic_aliases([1222284], ROTTING_PUSTULES),
    **mechanic_aliases([1287654], SPOREFALL),
    **mechanic_aliases([1222129], WRITHING_VINES),
}
