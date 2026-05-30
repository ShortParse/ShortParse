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


ENCOUNTER_ID = 3181
ENCOUNTER_NAME = "Crown of the Cosmos"

# ============================================================
# Crown of the Cosmos
# ============================================================

GRASP_OF_EMPTINESS: Mechanic = {
    "name": "Grasp of Emptiness",
    "severity": "Major",
    "avoidable": True,
    "category": "beam",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 40,
    "applies_to": ALL_ROLES,
    "spell_ids": [1260027],
    "note": (
        "Ancient obelisks grasp a player and fire beams outward when the effect ends."
    ),
    "recommendation": (
        "Aim the beams away from the raid and avoid standing in their path."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

BURSTING_EMPTINESS: Mechanic = {
    "name": "Bursting Emptiness",
    "severity": "Critical",
    "avoidable": True,
    "category": "beam",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "spell_ids": [1255378],
    "note": (
        "Void energy erupts outward from each obelisk in straight lines."
    ),
    "recommendation": (
        "Move out of the beam path before Bursting Emptiness detonates."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

VOID_EXPULSION: Mechanic = {
    "name": "Void Expulsion",
    "severity": "Major",
    "avoidable": True,
    "category": "swirl",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 35,
    "applies_to": ALL_ROLES,
    "spell_ids": [1233826],
    "note": (
        "Void orbs crash into the platform and create lingering void puddles."
    ),
    "recommendation": (
        "Move out of the impact swirl before detonation and bait puddles safely."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

VOID_REMNANTS: Mechanic = {
    "name": "Void Remnants",
    "severity": "Major",
    "avoidable": True,
    "category": "ground_effect",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 25,
    "applies_to": ALL_ROLES,
    "spell_ids": [1242553],
    "note": (
        "Lingering void puddles remain on the platform after Void Expulsion."
    ),
    "recommendation": (
        "Do not stand in Void Remnants puddles."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

INTERRUPTING_TREMOR: Mechanic = {
    "name": "Interrupting Tremor",
    "severity": "Info",
    "avoidable": True,
    "category": "forced_movement",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 15,
    "applies_to": ALL_ROLES,
    "spell_ids": [1243743],
    "note": (
        "The Sentinel releases a pulsing shockwave that damages and interrupts nearby players."
    ),
    "recommendation": (
        "Move out of range before Interrupting Tremor finishes casting."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

RAVENOUS_ABYSS: Mechanic = {
    "name": "Ravenous Abyss",
    "severity": "Major",
    "avoidable": True,
    "category": "boss_range",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 30,
    "applies_to": ALL_ROLES,
    "spell_ids": [1243753],
    "note": (
        "The Sentinel pulses damage and applies a heavy damage reduction debuff nearby."
    ),
    "recommendation": (
        "Move away from the Sentinel before Ravenous Abyss finishes casting."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

SILVERSTRIKE_BARRAGE: Mechanic = {
    "name": "Silverstrike Barrage",
    "severity": "Major",
    "avoidable": True,
    "category": "lane_movement",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 35,
    "applies_to": ALL_ROLES,
    "spell_ids": [1243981],
    "note": (
        "Waves of silver arrows travel across the platform in straight lines."
    ),
    "recommendation": (
        "Move into safe lanes between incoming arrows."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

ORBITING_MATTER: Mechanic = {
    "name": "Orbiting Matter",
    "severity": "Major",
    "avoidable": True,
    "category": "forced_movement",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 40,
    "applies_to": ALL_ROLES,
    "spell_ids": [1246001],
    "note": (
        "Orbiting masses pull players inward and deal heavy damage on contact."
    ),
    "recommendation": (
        "Avoid colliding with Orbiting Matter or getting pulled into it."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

SINGULARITY_ERUPTION: Mechanic = {
    "name": "Singularity Eruption",
    "severity": "Major",
    "avoidable": True,
    "category": "swirl",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 35,
    "applies_to": ALL_ROLES,
    "spell_ids": [1235631],
    "note": (
        "Gravity eruptions detonate at targeted locations and knock players away."
    ),
    "recommendation": (
        "Move out of Singularity Eruption impact swirls."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

VOLATILE_FISSURE: Mechanic = {
    "name": "Volatile Fissure",
    "severity": "Info",
    "avoidable": True,
    "category": "ground_effect",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 15,
    "applies_to": ALL_ROLES,
    "spell_ids": [1238210],
    "note": (
        "Crossing unstable platform fissures applies a stacking damage-over-time effect."
    ),
    "recommendation": (
        "Avoid crossing platform fissures unless necessary."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

DEVOURING_COSMOS: Mechanic = {
    "name": "Devouring Cosmos",
    "severity": "Critical",
    "avoidable": True,
    "category": "safe_zone",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "spell_ids": [1238882],
    "note": (
        "The platform is consumed by void energy during the transition."
    ),
    "recommendation": (
        "Collect a feather and move safely to the next platform."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

DARK_HAND: Mechanic = {
    "name": "Dark Hand",
    "severity": "Critical",
    "avoidable": False,
    "category": "tank_buster",
    "failure_type": "tank_failure",
    "counts_as_failure": False,
    "max_reasonable_hits": 0,
    "score_per_hit": 60,
    "applies_to": TANK_ONLY,
    "spell_ids": [1233787, 1233789],
    "note": (
        "Heavy tank strike dealing both Physical and Shadow damage with knockback."
    ),
    "recommendation": (
        "Use defensive cooldowns and prepare for knockback positioning."
    ),
    "wcl_type": "damage_taken",
    "mrt": False,
}

RIFT_SLASH: Mechanic = {
    "name": "Rift Slash",
    "severity": "Major",
    "avoidable": False,
    "category": "tank_buster",
    "failure_type": "tank_failure",
    "counts_as_failure": False,
    "max_reasonable_hits": 3,
    "score_per_hit": 30,
    "applies_to": TANK_ONLY,
    "spell_ids": [1246461],
    "note": (
        "Heavy tank strike that applies a stacking stat reduction debuff."
    ),
    "recommendation": (
        "Tank swap appropriately to manage Rift Slash stacks."
    ),
    "wcl_type": "damage_taken",
    "mrt": False,
}

# Add unmapped mechanics
ECHOING_DARKNESS: Mechanic = {
    "name": "Echoing Darkness",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Echoing Darkness deals ticking shadow damage in active areas.",
    "recommendation": "Step out of Echoing Darkness zones immediately.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

VOIDSTALKER_STING: Mechanic = {
    "name": "Voidstalker Sting",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Avoid getting hit by Voidstalker Sting projectiles.",
    "recommendation": "Dodge traveling Voidstalker Sting missiles.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

SIMULACRUM_BACKLASH: Mechanic = {
    "name": "Simulacrum Backlash",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Devastating shadow damage when the Simulacrum shatters.",
    "recommendation": "Move away from the Simulacrum before it shatters.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

COSMIC_BARRIER: Mechanic = {
    "name": "Cosmic Barrier",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Cosmic Barrier deal ticking shadow damage to players inside.",
    "recommendation": "Avoid standing inside active Cosmic Barrier fields.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

STELLAR_EMISSION: Mechanic = {
    "name": "Stellar Emission",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Stellar Emission launches ticking shadow flares.",
    "recommendation": "Avoid stellar flares on the ground.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

COSMIC_RADIATION: Mechanic = {
    "name": "Cosmic Radiation",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Avoid getting hit by cosmic radiation swirls.",
    "recommendation": "Step out of Cosmic Radiation impact zones.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

VOID_BARRAGE: Mechanic = {
    "name": "Void Barrage",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Continuous shadow missiles fired at players.",
    "recommendation": "Dodge incoming void barrage projectiles.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

SILVERSTRIKE_RICOCHET: Mechanic = {
    "name": "Silverstrike Ricochet",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Silverstrike arrows ricochet between nearby targets.",
    "recommendation": "Spread out to avoid ricochets.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

SILVERSTRIKE_ARROW: Mechanic = {
    "name": "Silverstrike Arrow",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Fired arrow deal high piercing damage.",
    "recommendation": "Step away from arrow paths.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

GRAVITY_COLLAPSE: Mechanic = {
    "name": "Gravity Collapse",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": "Gravity collapse deals severe damage and knocks down players.",
    "recommendation": "Step out of Gravity Collapse zones.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

AVOIDABLE_DAMAGE = {
    **mechanic_aliases([1260027], GRASP_OF_EMPTINESS),
    **mechanic_aliases([1255378], BURSTING_EMPTINESS),
    **mechanic_aliases([1233826], VOID_EXPULSION),
    **mechanic_aliases([1242553], VOID_REMNANTS),
    **mechanic_aliases([1243743], INTERRUPTING_TREMOR),
    **mechanic_aliases([1243753], RAVENOUS_ABYSS),
    **mechanic_aliases([1243981], SILVERSTRIKE_BARRAGE),
    **mechanic_aliases([1246001], ORBITING_MATTER),
    **mechanic_aliases([1235631], SINGULARITY_ERUPTION),
    **mechanic_aliases([1238210], VOLATILE_FISSURE),
    **mechanic_aliases([1238882], DEVOURING_COSMOS),
    **mechanic_aliases([1233787, 1233789], DARK_HAND),
    **mechanic_aliases([1246461], RIFT_SLASH),
    **mechanic_aliases([1281707], ECHOING_DARKNESS),
    **mechanic_aliases([1237040], VOIDSTALKER_STING),
    **mechanic_aliases([1260019], SIMULACRUM_BACKLASH),
    **mechanic_aliases([1261289], COSMIC_BARRIER),
    **mechanic_aliases([1234570], STELLAR_EMISSION),
    **mechanic_aliases([1260771], COSMIC_RADIATION),
    **mechanic_aliases([1260000], VOID_BARRAGE),
    **mechanic_aliases([1259869], SILVERSTRIKE_RICOCHET),
    **mechanic_aliases([1233649], SILVERSTRIKE_ARROW),
    **mechanic_aliases([1239095], GRAVITY_COLLAPSE),
}