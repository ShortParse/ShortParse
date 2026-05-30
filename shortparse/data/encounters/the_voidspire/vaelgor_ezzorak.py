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
    "mrt": True,
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
    "mrt": True,
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
    "mrt": True,
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
    "mrt": True,
}

# Add unmapped mechanics
MIDNIGHT_MANIFESTATION: Mechanic = {
    "name": "Midnight Manifestation",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Avoid standing in the Midnight Manifestation impact zones.",
    "recommendation": "Step away from Midnight Manifestation impact areas.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

NULLZONE_IMPLOSION: Mechanic = {
    "name": "Nullzone Implosion",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Raid takes heavy damage when Nullzones implode.",
    "recommendation": "Move out of Nullzone Implosion zones.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

VOID_HOWL: Mechanic = {
    "name": "Void Howl",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Boss lets out a void howl dealing avoidable raid-wide damage.",
    "recommendation": "Use defensive cooldowns or avoid the void howl.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

NULLSNAP: Mechanic = {
    "name": "Nullsnap",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Avoid getting hit by Nullsnap snap tethers.",
    "recommendation": "React quickly to snap tethers.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

VOIDBOLT: Mechanic = {
    "name": "Voidbolt",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Avoid getting hit by Voidbolts fired by adds.",
    "recommendation": "Dodge traveling Voidbolts.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

GLOOMTOUCHED: Mechanic = {
    "name": "Gloomtouched",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Gloomtouched explosions deal severe avoidable damage.",
    "recommendation": "Step out of Gloomtouched detonation circles.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

NULLZONE: Mechanic = {
    "name": "Nullzone",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Nullzone pools deal ticking shadow damage.",
    "recommendation": "Do not stand inside active Nullzones.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

SHADOWMARK: Mechanic = {
    "name": "Shadowmark",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Players marked by Shadowmark take avoidable detonation damage.",
    "recommendation": "Step out of the Shadowmark group.",
    "wcl_type": "damage_taken",
    "mrt": True,
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
    "mrt": True,
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
    "mrt": True,
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
    "mrt": True,
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
    "mrt": True,
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
    "mrt": True,
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
    "mrt": False,
}

AVOIDABLE_DAMAGE = {
    **mechanic_aliases([1264467], TAIL_LASH),
    **mechanic_aliases([1265152], IMPALE),
    **mechanic_aliases([1265139, 1280434, 1265143], VAELWING),
    **mechanic_aliases([1245652, 1245647], RAKFANG),
    **mechanic_aliases([1266570], NULLSCATTER),
    **mechanic_aliases([1249748, 1250071], MIDNIGHT_FLAMES),
    **mechanic_aliases([1245421], GLOOMFIELD),
    **mechanic_aliases([1245500], GLOOM),
    **mechanic_aliases([1244225, 1255979], DREAD_BREATH),
    **mechanic_aliases([1283856, 1262688], NULLBEAM),
    **mechanic_aliases([1259275], MIDNIGHT_MANIFESTATION),
    **mechanic_aliases([1285954, 1252157], NULLZONE_IMPLOSION),
    **mechanic_aliases([1245302], VOID_HOWL),
    **mechanic_aliases([1244413], NULLSNAP),
    **mechanic_aliases([1245175], VOIDBOLT),
    **mechanic_aliases([1283712, 1283711], GLOOMTOUCHED),
    **mechanic_aliases([1244672], NULLZONE),
    **mechanic_aliases([1270513, 1270516], SHADOWMARK),
}