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

ENCOUNTER_ID = 3177
ENCOUNTER_NAME = "Vorasius"

FALLING: Mechanic = {
    "name": "Falling",
    "severity": "Critical",
    "avoidable": True,
    "category": "forced_movement",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "note": (
        "The boss will attempt to pull players off the platform."
    ),
    "recommendation": (
        "Position carefully to avoid being pulled off the platform."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

SHADOWCLAW_SLAM: Mechanic = {
    "name": "Shadowclaw Slam",
    "severity": "Critical",
    "avoidable": True,
    "category": "tank_buster",
    "failure_type": "avoidable_damage",
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
    "mrt": False,
}

VOID_BREATH: Mechanic = {
    "name": "Void Breath",
    "severity": "Critical",
    "avoidable": True,
    "category": "beam",
    "failure_type": "avoidable_damage",
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
    "mrt": True,
}

OVERPOWERING_PULSE: Mechanic = {
    "name": "Overpowering Pulse",
    "severity": "Critical",
    "avoidable": True,
    "category": "boss_range",
    "failure_type": "boss_range",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": TANK_ONLY,
    "note": (
        "Vorasius deals lethal raid-wide damage if no player is within melee range."
    ),
    "recommendation": (
        "At least one tank must remain in melee range at all times."
    ),
    "wcl_type": "damage_taken",
    "mrt": False,
}

AFTERSHOCK: Mechanic = {
    "name": "Aftershock",
    "severity": "Critical",
    "avoidable": True,
    "category": "ground_effect",
    "failure_type": "avoidable_damage",
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
    "mrt": True,
}

DARK_GOO: Mechanic = {
    "name": "Dark Goo",
    "severity": "Warning",
    "avoidable": True,
    "category": "corpse_explosion",
    "failure_type": "avoidable_damage",
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
    "mrt": True,
}

PARASITE_EXPULSION: Mechanic = {
    "name": "Parasite Expulsion",
    "severity": "Critical",
    "avoidable": True,
    "category": "swirl",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": (
        "The boss will frequently spray globs of dark ichor across the battlefield."
    ),
    "recommendation": (
        "Move out of the impact swirl before detonation."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

BLISTERBURST: Mechanic = {
    "name": "Blisterburst",
    "severity": "Warning",
    "avoidable": True,
    "category": "add_management",
    "failure_type": "avoidable_damage",
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
    "mrt": True,
}

PRIMORDIAL_POWER: Mechanic = {
    "name": "Primordial Power",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Avoid standing in the Primordial Power zone.",
    "recommendation": "Step away from Primordial Power impact areas.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

DARK_ENERGY: Mechanic = {
    "name": "Dark Energy",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Raid takes dark energy damage when circles detonate.",
    "recommendation": "Move out of Dark Energy detonation zones.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

PRIMORDIAL_ROAR: Mechanic = {
    "name": "Primordial Roar",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Boss lets out a massive roar dealing avoidable shadow damage.",
    "recommendation": "Check positioning to mitigate or avoid roar damage.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

AVOIDABLE_DAMAGE = {
    **mechanic_aliases([3], FALLING),
    **mechanic_aliases([1281954, 1281906, 1272328, 1241808], SHADOWCLAW_SLAM),
    **mechanic_aliases([1257607, 1259923, 1259921], VOID_BREATH),
    **mechanic_aliases([1244419], OVERPOWERING_PULSE),
    **mechanic_aliases([1276584, 1276828, 1276583, 1276829, 1276824, 1276581, 1276588, 1276830, 1276832, 1276812, 1276811, 1276833, 1276834, 1276813, 1276835, 1276817], AFTERSHOCK),
    **mechanic_aliases([1243270], DARK_GOO),
    **mechanic_aliases([1275558, 1275556], PARASITE_EXPULSION),
    **mechanic_aliases([1259186, 1269302], BLISTERBURST),
    **mechanic_aliases([1272950], PRIMORDIAL_POWER),
    **mechanic_aliases([1280101], DARK_ENERGY),
    **mechanic_aliases([1260052], PRIMORDIAL_ROAR),
}