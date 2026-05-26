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


ENCOUNTER_ID = 3178
ENCOUNTER_NAME = "Vaelgor & Ezzorak"

TAIL_LASH: Mechanic = {
    "name": "Tail Lash",
    "severity": "Warning",
    "avoidable": True,
    "category": "rear_cone",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 30,
    "applies_to": ALL_ROLES,
    "note": (
        "Vaelgor knocks away players within a 35 yard rear cone."
    ),
    "recommendation": (
        "Review movement pathing and avoid standing behind Vaelgor."
    ),
    "wcl_type": "damage_taken",
}

IMPALE: Mechanic = {
    "name": "Impale",
    "severity": "Warning",
    "avoidable": True,
    "category": "rear_cone",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 30,
    "applies_to": ALL_ROLES,
    "note": (
        "Ezzorak slams targets within a 35 yard rear cone."
    ),
    "recommendation": (
        "Review movement pathing and avoid standing behind Ezzorak."
    ),
    "wcl_type": "damage_taken",
}

VAELWING: Mechanic = {
    "name": "Vaelwing",
    "severity": "Major",
    "avoidable": True,
    "category": "boss_threat",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 100,
    "applies_to": NON_TANK_ROLES,
    "note": (
        "Vaelgor buffets his primary target."
    ),
    "recommendation": (
        "Avoid taking threat from the tank."
    ),
    "wcl_type": "damage_taken",
}

RAKFANG: Mechanic = {
    "name": "Rakfang",
    "severity": "Major",
    "avoidable": True,
    "category": "boss_threat",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 100,
    "applies_to": NON_TANK_ROLES,
    "note": (
        "Ezzorak strikes his primary target."
    ),
    "recommendation": (
        "Avoid taking threat from the tank."
    ),
    "wcl_type": "damage_taken",
}

NULLSCATTER: Mechanic = {
    "name": "Nullscatter",
    "severity": "Critical",
    "avoidable": True,
    "category": "swirl",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": (
        "Nullzone's first tether snap releases a cascade of cosmic hail."
    ),
    "recommendation": (
        "Move out of the impact swirl before detonation."
    ),
    "wcl_type": "damage_taken",
}

MIDNIGHT_FLAMES: Mechanic = {
    "name": "Midnight Flames",
    "severity": "Critical",
    "avoidable": True,
    "category": "safe_zone",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "note": (
        "Upon reaching 100 energy, Vaelgor and Ezzorak fly as one."
    ),
    "recommendation": (
        "Review movement pathing and stay in the safe-zone bubble."
    ),
    "wcl_type": "damage_taken",
}

GLOOMFIELD: Mechanic = {
    "name": "Gloomfield",
    "severity": "Major",
    "avoidable": True,
    "category": "ground_effect",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 60,
    "applies_to": ALL_ROLES,
    "note": (
        "Galactic emptiness engulfs a massive location in darkness."
    ),
    "recommendation": (
        "Review movement pathing and avoid the impact zones."
    ),
    "wcl_type": "damage_taken",
}

GLOOM: Mechanic = {
    "name": "Gloom",
    "severity": "Critical",
    "avoidable": False,
    "category": "minimum_soak",
    "failure_type": "minimum_soak",
    "counts_as_failure": False,
    "minimum_soakers": 5,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "spell_ids": [1245500],
    "note": (
        "Ezzorak fires a moving orb of darkness. At least 5 players must soak it "
        "to minimize the platform denial when it reaches the edge."
    ),
    "recommendation": (
        "Assign 5 players to soak each Gloom orb. Avoid sending extra players "
        "because additional soakers take damage without reducing the zone further."
    ),
    "wcl_type": "damage_taken",
}

DREAD_BREATH: Mechanic = {
    "name": "Dread Breath",
    "severity": "Critical",
    "avoidable": True,
    "category": "beam",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "note": (
        "Vaelgor targets a player with a massive frontal breath. The targeted player "
        "must aim it away from the raid."
    ),
    "recommendation": (
        "Targeted players should aim Dread Breath away from the raid. Non-targeted "
        "players should move away from the targeted player and avoid the frontal."
    ),
    "wcl_type": "damage_taken",
}

NULLBEAM: Mechanic = {
    "name": "Nullbeam",
    "severity": "Critical",
    "avoidable": True,
    "category": "tank_buster",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": NON_TANK_ROLES,
    "note": (
        "Nullbeam should be aimed into the active tank only. Non-tanks hit by the beam are taking avoidable tank mechanic damage."
    ),
    "recommendation": (
        "Non-tanks should avoid standing in the Nullbeam frontal."
    ),
    "wcl_type": "damage_taken",
}



AVOIDABLE_DAMAGE = {
    **mechanic_aliases([1264467], TAIL_LASH),
    **mechanic_aliases([1265152], IMPALE),
    **mechanic_aliases([1265139], VAELWING),
    **mechanic_aliases([1245652, 1245647], RAKFANG),
    **mechanic_aliases([1266570], NULLSCATTER),
    **mechanic_aliases([1249748], MIDNIGHT_FLAMES),
    **mechanic_aliases([1245421], GLOOMFIELD),
    **mechanic_aliases([1245500], GLOOM),
    **mechanic_aliases([1244225], DREAD_BREATH),
    **mechanic_aliases([1283856], NULLBEAM),
}