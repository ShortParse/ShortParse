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

ENCOUNTER_ID = 3179
ENCOUNTER_NAME = "Fallen-King Salhadaar"

VOID_INFUSION: Mechanic = {
    "name": "Void Infusion",
    "severity": "Critical",
    "avoidable": True,
    "category": "add_priority",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "note": (
        "Orbs must be killed before the boss can absorb them."
    ),
    "recommendation": (
        "Focus fire one orb, and then the remaining orb."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

SHADOW_FRACTURE: Mechanic = {
    "name": "Shadow Fracture",
    "severity": "Major",
    "avoidable": True,
    "category": "interrupt",
    "failure_type": "missed_interrupt",
    "counts_as_failure": True,
    "max_reasonable_hits": 4,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": (
        "Adds cast Shadow Fracture which must be stopped."
    ),
    "recommendation": (
        "Stop the adds from casting with an interrupt."
    ),
    "wcl_type": "cast events",
    "mrt": True,
}

UMBRAL_BEAMS: Mechanic = {
    "name": "Umbral Beams",
    "severity": "Critical",
    "avoidable": True,
    "category": "beam",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "note": (
        "Boss spins in a circle, shooting out laser beams."
    ),
    "recommendation": (
        "Avoid touching the laser beams."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

DESPOTIC_COMMAND: Mechanic = {
    "name": "Despotic Command",
    "severity": "Major",
    "avoidable": True,
    "category": "spread",
    "failure_type": "spread_failure",
    "counts_as_failure": True,
    "max_reasonable_hits": 10,
    "score_per_hit": 50,
    "applies_to": ALL_ROLES,
    "note": (
        "Players pulse damage in a circle around them for 12s."
    ),
    "recommendation": (
        "Spread out and do not be in another players circle."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

TWILIGHT_SPIKES: Mechanic = {
    "name": "Twilight Spikes",
    "severity": "Major",
    "avoidable": True,
    "category": "spread_failure",
    "failure_type": "spread_out",
    "counts_as_failure": True,
    "max_reasonable_hits": 4,
    "score_per_hit": 30,
    "applies_to": ALL_ROLES,
    "note": (
        "Players are marked, and then explode shooting out spikes."
    ),
    "recommendation": (
        "Check positioning and avoid spikes."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

TORTURUS_EXTRACT: Mechanic = {
    "name": "Torturous Extract",
    "severity": "Info",
    "avoidable": True,
    "category": "ground_effect",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 3,
    "score_per_hit": 10,
    "applies_to": ALL_ROLES,
    "note": (
        "Players drop void pools, standing in them does damage."
    ),
    "recommendation": (
        "Review movement pathing and avoid the impact zones."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

DESTABILIZING_STRIKES: Mechanic = {
    "name": "Destabilizing Strikes",
    "severity": "Info",
    "avoidable": True,
    "category": "boss_threat",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 10,
    "applies_to": NON_TANK_ROLES,
    "note": (
        "This attack should only hit the tanks."
    ),
    "recommendation": (
        "Avoid taking threat from the boss."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

VOID_CRUSH: Mechanic = {
    "name": "Void Crush",
    "severity": "Info",
    "avoidable": True,
    "category": "forced_movement",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 20,
    "applies_to": ALL_ROLES,
    "note": (
        "Orbs draw players in, then knock then back with big damage."
    ),
    "recommendation": (
        "Avoid getting pulled into the orbs."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

QUINTESSENCE: Mechanic = {
    "name": "Quintessence",
    "severity": "Major",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "ground_effect",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 20,
    "applies_to": ALL_ROLES,
    "note": (
        "Boss lobs several missiles at the ground."
    ),
    "recommendation": (
        "Review movement pathing and avoid the impact zones."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

TWISTING_OBSCURITY: Mechanic = {
    "name": "Twisting Obscurity",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Avoid standing in the Twisting Obscurity zones on the ground.",
    "recommendation": "Step away from Twisting Obscurity pools.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

DARK_RADIATION: Mechanic = {
    "name": "Dark Radiation",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Raid takes high damage when Dark Radiation bursts.",
    "recommendation": "Move out of Dark Radiation impact areas.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

ENTROPIC_UNRAVELING: Mechanic = {
    "name": "Entropic Unraveling",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Entropic Unraveling pools deal ticking damage.",
    "recommendation": "Step out of Entropic Unraveling zones immediately.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

VOID_EXPOSURE: Mechanic = {
    "name": "Void Exposure",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Players marked by Void Exposure take ticking void damage.",
    "recommendation": "Step out of active Void Exposure zones.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

SHATTERING_TWILIGHT: Mechanic = {
    "name": "Shattering Twilight",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Avoid standing in the Shattering Twilight blast zone.",
    "recommendation": "Step away from Shattering Twilight circles.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

AVOIDABLE_DAMAGE = {
    **mechanic_aliases([1245960], VOID_INFUSION),
    **mechanic_aliases([1254088], SHADOW_FRACTURE),
    **mechanic_aliases([1260030], UMBRAL_BEAMS),
    **mechanic_aliases([1260835], DESPOTIC_COMMAND),
    **mechanic_aliases([1251213], TWILIGHT_SPIKES),
    **mechanic_aliases([1245592], TORTURUS_EXTRACT),
    **mechanic_aliases([1284963], DESTABILIZING_STRIKES),
    **mechanic_aliases([1239667], VOID_CRUSH),
    **mechanic_aliases([1246094], QUINTESSENCE),
    **mechanic_aliases([1250686], TWISTING_OBSCURITY),
    **mechanic_aliases([1285504], DARK_RADIATION),
    **mechanic_aliases([1254018], ENTROPIC_UNRAVELING),
    **mechanic_aliases([1250828], VOID_EXPOSURE),
    **mechanic_aliases([1262989, 1250803], SHATTERING_TWILIGHT),
}