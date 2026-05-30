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

ENCOUNTER_ID = 3183
ENCOUNTER_NAME = "Midnight Falls"

# ============================================================
# L'ura - Midnight Falls
# ============================================================

DEATHS_DIRGE: Mechanic = {
    "name": "Death's Dirge",
    "severity": "Major",
    "avoidable": True,
    "category": "memory_game",
    "failure_type": "incorrect_sequence",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 40,
    "applies_to": ALL_ROLES,
    "spell_ids": [1249594],
    "note": (
        "Incorrect rune sequencing during Death's Dirge."
    ),
    "recommendation": (
        "Match rune order correctly during the memory sequence."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

DISSONANCE: Mechanic = {
    "name": "Dissonance",
    "severity": "Critical",
    "avoidable": True,
    "category": "memory_failure",
    "failure_type": "incorrect_sequence",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "spell_ids": [1249585],
    "note": (
        "Raid failed the rune sequence order."
    ),
    "recommendation": (
        "Players must execute rune order correctly."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

TERMINATE: Mechanic = {
    "name": "Terminate",
    "severity": "Critical",
    "avoidable": True,
    "category": "interrupt",
    "failure_type": "missed_interrupt",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 90,
    "applies_to": ALL_ROLES,
    "spell_ids": [1286276],
    "note": (
        "Termination Matrix cast completed."
    ),
    "recommendation": (
        "Interrupt Terminate casts immediately."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

COSMIC_FRACTURE: Mechanic = {
    "name": "Cosmic Fracture",
    "severity": "Critical",
    "avoidable": True,
    "category": "add_failure",
    "failure_type": "failed_add_kill",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "spell_ids": [1251789],
    "note": (
        "Midnight Crystal was not destroyed in time."
    ),
    "recommendation": (
        "Kill Midnight Crystals before Cosmic Fracture completes."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

NAARUS_LAMENT: Mechanic = {
    "name": "Naaru's Lament",
    "severity": "Critical",
    "avoidable": True,
    "category": "missed_soak",
    "failure_type": "failed_soak",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "spell_ids": [1254256, 1254257],
    "note": (
        "Tears of L'ura soak failed."
    ),
    "recommendation": (
        "Ensure every Tear of L'ura is soaked."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

GALVANIZE: Mechanic = {
    "name": "Galvanize",
    "severity": "Major",
    "avoidable": True,
    "category": "line_soak",
    "failure_type": "failed_line_soak",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 50,
    "applies_to": ALL_ROLES,
    "spell_ids": [1284530],
    "note": (
        "Galvanize beam improperly soaked or aimed."
    ),
    "recommendation": (
        "Aim Galvanize into assigned Void Cores with proper soak groups."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

OVERKILL_CURRENT: Mechanic = {
    "name": "Overkill Current",
    "severity": "Major",
    "avoidable": True,
    "category": "soak_failure",
    "failure_type": "insufficient_soak",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 70,
    "applies_to": ALL_ROLES,
    "spell_ids": [1285827],
    "note": (
        "Too few players soaked Galvanize."
    ),
    "recommendation": (
        "Assigned groups must stack inside Galvanize."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

COSMIC_FISSION: Mechanic = {
    "name": "Cosmic Fission",
    "severity": "Major",
    "avoidable": True,
    "category": "movement",
    "failure_type": "pull_failure",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 40,
    "applies_to": ALL_ROLES,
    "spell_ids": [1282372],
    "note": (
        "Player took excessive Cosmic Fission damage."
    ),
    "recommendation": (
        "Position safely during Void Core pulls."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

CHARGED_CORE: Mechanic = {
    "name": "Charged Core",
    "severity": "Critical",
    "avoidable": True,
    "category": "orb_contact",
    "failure_type": "touched_orb",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 90,
    "applies_to": ALL_ROLES,
    "spell_ids": [1282375],
    "note": (
        "Player touched a Charged Core."
    ),
    "recommendation": (
        "Avoid contact with Charged Cores."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

DARK_QUASAR: Mechanic = {
    "name": "Dark Quasar",
    "severity": "Critical",
    "avoidable": True,
    "category": "beam",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "spell_ids": [1282469],
    "note": (
        "Player was hit by rotating Darkwell beams."
    ),
    "recommendation": (
        "Avoid Dark Quasar beams."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

HEAVENS_GLAIVES: Mechanic = {
    "name": "Heaven's Glaives",
    "severity": "Major",
    "avoidable": True,
    "category": "movement",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 35,
    "applies_to": ALL_ROLES,
    "spell_ids": [1254076],
    "note": (
        "Player was struck by bouncing glaives."
    ),
    "recommendation": (
        "Dodge ricocheting glaives."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

STARSPLINTER: Mechanic = {
    "name": "Starsplinter",
    "severity": "Major",
    "avoidable": True,
    "category": "spread",
    "failure_type": "failed_spread",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 50,
    "applies_to": ALL_ROLES,
    "spell_ids": [1281473, 1279581],
    "note": (
        "Starsplinter explosion hit nearby players."
    ),
    "recommendation": (
        "Spread properly for Starsplinter impacts."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

LIGHTS_END: Mechanic = {
    "name": "Light's End",
    "severity": "Critical",
    "avoidable": True,
    "category": "crystal_failure",
    "failure_type": "destroyed_crystal",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 150,
    "applies_to": ALL_ROLES,
    "spell_ids": [1284699],
    "note": (
        "A Dawn Crystal was destroyed."
    ),
    "recommendation": (
        "Protect Dawn Crystals from Cosmic damage."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

DECAY: Mechanic = {
    "name": "Decay",
    "severity": "Critical",
    "avoidable": True,
    "category": "phase_failure",
    "failure_type": "failed_core_management",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 120,
    "applies_to": ALL_ROLES,
    "spell_ids": [1284531],
    "note": (
        "Remaining Void Cores detonated."
    ),
    "recommendation": (
        "Destroy all Void Cores before phase end."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

DARK_MELTDOWN: Mechanic = {
    "name": "Dark Meltdown",
    "severity": "Critical",
    "avoidable": True,
    "category": "phase_failure",
    "failure_type": "phase_timeout",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 150,
    "applies_to": ALL_ROLES,
    "spell_ids": [1281123],
    "note": (
        "L'ura reached 100 energy."
    ),
    "recommendation": (
        "Complete Void Core phase before energy cap."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

DARK_CONSTELLATION: Mechanic = {
    "name": "Dark Constellation",
    "severity": "Major",
    "avoidable": False,
    "category": "movement",
    "failure_type": "avoidable_damage",
    "counts_as_failure": False,
    "max_reasonable_hits": 2,
    "score_per_hit": 40,
    "applies_to": ALL_ROLES,
    "spell_ids": [1282004],
    "note": (
        "Player stood in Dark Constellation patterns."
    ),
    "recommendation": (
        "Move between constellation lines safely."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}


LIGHT_SIPHON: Mechanic = {
    "name": "Light Siphon",
    "severity": "Critical",
    "avoidable": True,
    "category": "soak",
    "failure_type": "failed_soak",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "spell_ids": [1282458],
    "note": (
        "Light Siphon soak circle was not fully drained, triggering a Stellar Implosion."
    ),
    "recommendation": (
        "Stand inside Light Siphon circles until completely removed."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

DARK_ARCHANGEL: Mechanic = {
    "name": "Dark Archangel",
    "severity": "Critical",
    "avoidable": False,
    "category": "shield_requirement",
    "failure_type": "missing_barrier",
    "counts_as_failure": False,
    "max_reasonable_hits": 1,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "spell_ids": [1254644],
    "note": (
        "Raid failed to properly use Dawnlight Barrier."
    ),
    "recommendation": (
        "Use Dawn Crystal barrier during Dark Archangel."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

MIDNIGHT: Mechanic = {
    "name": "Midnight",
    "severity": "Critical",
    "avoidable": True,
    "category": "positioning",
    "failure_type": "out_of_light",
    "counts_as_failure": True,
    "max_reasonable_hits": 2,
    "score_per_hit": 60,
    "applies_to": ALL_ROLES,
    "spell_ids": [1254398],
    "note": (
        "Player stood outside Torchbearer light radius."
    ),
    "recommendation": (
        "Stay near Dawn Crystal holders."
    ),
    "wcl_type": "damage_taken",
    "mrt": True,
}

SHATTERED_SKY: Mechanic = {
    "name": "Shattered Sky",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "spell_ids": [1249797],
    "note": "Player took avoidable damage from Shattered Sky.",
    "recommendation": "Move out of the Shattered Sky impact zones immediately.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

HEAVENS_LANCE: Mechanic = {
    "name": "Heaven's Lance",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 75,
    "applies_to": ALL_ROLES,
    "spell_ids": [1253878],
    "note": "Player hit by Heaven's Lance projectile.",
    "recommendation": "Dodge the trajectory of Heaven's Lance.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

IMPALED: Mechanic = {
    "name": "Impaled",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 75,
    "applies_to": ALL_ROLES,
    "spell_ids": [1253879],
    "note": "Player was impaled by failing to dodge spikes or lances.",
    "recommendation": "Dodge ground spikes and boss lances to avoid being Impaled.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

DISINTEGRATION: Mechanic = {
    "name": "Disintegration",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 70,
    "applies_to": ALL_ROLES,
    "spell_ids": [1251649],
    "note": "Player hit by Disintegration beam.",
    "recommendation": "Step out of the Disintegration beam immediately.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

CORE_HARVEST: Mechanic = {
    "name": "Core Harvest",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "spell_ids": [1282425],
    "note": "Player hit by Core Harvest explosion.",
    "recommendation": "Move away from harvesting cores to avoid damage.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

CRITICALITY: Mechanic = {
    "name": "Criticality",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 75,
    "applies_to": ALL_ROLES,
    "spell_ids": [1281178],
    "note": "Player failed to manage energy or stood in Criticality zones.",
    "recommendation": "Avoid standing in high energy Criticality impact zones.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

RESONANCE: Mechanic = {
    "name": "Resonance",
    "severity": "Critical",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 70,
    "applies_to": ALL_ROLES,
    "spell_ids": [1249582],
    "note": "Player took damage from Resonance due to wrong color or poor positioning.",
    "recommendation": "Position correctly to avoid Resonance waves.",
    "wcl_type": "damage_taken",
    "mrt": True,
}

DIMMING: Mechanic = {
    "name": "Dimming",
    "severity": "Major",
    "avoidable": True,
    "category": "avoidable_damage",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 55,
    "applies_to": ALL_ROLES,
    "spell_ids": [1252975],
    "note": "Player hit by Dimming projectile or stood in Dimming circle.",
    "recommendation": "Avoid the fading light paths and Dimming circles.",
    "wcl_type": "damage_taken",
    "mrt": True,
}


AVOIDABLE_DAMAGE = {
    **mechanic_aliases([1249594], DEATHS_DIRGE),
    **mechanic_aliases([1249585], DISSONANCE),
    **mechanic_aliases([1286276], TERMINATE),
    **mechanic_aliases([1251789], COSMIC_FRACTURE),
    **mechanic_aliases([1254256, 1254257], NAARUS_LAMENT),
    **mechanic_aliases([1284530], GALVANIZE),
    **mechanic_aliases([1285827], OVERKILL_CURRENT),
    **mechanic_aliases([1282372], COSMIC_FISSION),
    **mechanic_aliases([1282375], CHARGED_CORE),
    **mechanic_aliases([1282469], DARK_QUASAR),
    **mechanic_aliases([1254076], HEAVENS_GLAIVES),
    **mechanic_aliases([1281473, 1279581], STARSPLINTER),
    **mechanic_aliases([1284699], LIGHTS_END),
    **mechanic_aliases([1284531], DECAY),
    **mechanic_aliases([1281123], DARK_MELTDOWN),
    **mechanic_aliases([1282458], LIGHT_SIPHON),
    **mechanic_aliases([1254644], DARK_ARCHANGEL),
    **mechanic_aliases([1254398], MIDNIGHT),
    **mechanic_aliases([1282004], DARK_CONSTELLATION),
    **mechanic_aliases([1249797], SHATTERED_SKY),
    **mechanic_aliases([1253878], HEAVENS_LANCE),
    **mechanic_aliases([1253879], IMPALED),
    **mechanic_aliases([1251649], DISINTEGRATION),
    **mechanic_aliases([1282425], CORE_HARVEST),
    **mechanic_aliases([1281178], CRITICALITY),
    **mechanic_aliases([1249582], RESONANCE),
    **mechanic_aliases([1252975], DIMMING),
}
