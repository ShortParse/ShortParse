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


ENCOUNTER_ID = 3179
ENCOUNTER_NAME = "Fallen-King Salhadaar"

VOID_INFUSION = {
    "name": "Void Infusion",
    "severity": "Critical",
    "avoidable": True,
    "category": "Boss Kite",
    "failure_type": "dodge_adds",
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
}

SHADOW_FRACTURE = {
    "name": "Shadow Fracture",
    "severity": "Major",
    "avoidable": True,
    "category": "Interrupt",
    "failure_type": "interrupt_adds",
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
    "wcl_type": "damage_taken",
}

UMBRAL_BEAMS = {
    "name": "Umbral Beams",
    "severity": "Critical",
    "avoidable": True,
    "category": "Dodge Lines",
    "failure_type": "dodge_oneshot",
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
}

DESPOTIC_COMMAND = {
    "name": "Despotic Command",
    "severity": "Major",
    "avoidable": True,
    "category": "Spread Out",
    "failure_type": "spread_out",
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
}

TWILIGHT_SPIKES = {
    "name": "Twilight Spikes",
    "severity": "Major",
    "avoidable": True,
    "category": "Spread Out",
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
}

TORTURUS_EXTRACT = {
    "name": "Torturous Extract",
    "severity": "Info",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "ground_effect",
    "counts_as_failure": True,
    "max_reasonable_hits": 3,
    "score_per_hit": 10,
    "applies_to": ALL_ROLES,
    "note": (
        "Players drop void pools, standing in them does damage."
    ),
    "recommendation": (
        "Check positioning and avoid standing in void pools."
    ),
    "wcl_type": "damage_taken",
}

DESTABILIZING_STRIKES = {
    "name": "Destabilizing Strikes",
    "severity": "Info",
    "avoidable": True,
    "category": "Boss Threat",
    "failure_type": "boss_threat",
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
}

VOID_CRUSH = {
    "name": "Void Crush",
    "severity": "Info",
    "avoidable": True,
    "category": "Gravity Pull",
    "failure_type": "dodge_gravity",
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
}

QUINTESSENCE = {
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
        "Avoid standing in the ground missles."
    ),
    "wcl_type": "damage_taken",
}

AVOIDABLE_DAMAGE = {
    # Void Infusion
    **mechanic_aliases(
        [1245960],
        VOID_INFUSION,
    ),
    # Shadow Fracture
    **mechanic_aliases(
        [1254088],
        SHADOW_FRACTURE,
    ),
    # Umbral Beams
    **mechanic_aliases(
        [1260030],
        UMBRAL_BEAMS,
    ),
    # Despotic Command
    **mechanic_aliases(
        [1260835],
        SHADOW_FRACTURE,
    ),
    # Twilight Spikes
    **mechanic_aliases(
        [1251213],
        TWILIGHT_SPIKES,
    ),
    # Torturous Extract
    **mechanic_aliases(
        [1245592],
        TORTURUS_EXTRACT,
    ),
    # Destabilizing Strikes
    **mechanic_aliases(
        [1284963],
        DESTABILIZING_STRIKES,
    ),
    # Void Crush
    **mechanic_aliases(
        [1239667],
        VOID_CRUSH,
    ),
    # Quintessence
    **mechanic_aliases(
        [1246094],
        QUINTESSENCE,
    ),
}