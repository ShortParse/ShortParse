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
    "spell_ids": [1254256],
    "note": (
        "Tears of L'ura soak failed."
    ),
    "recommendation": (
        "Ensure every Tear of L'ura is soaked."
    ),
    "wcl_type": "damage_taken",
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
}


AVOIDABLE_DAMAGE = {
    **mechanic_aliases([1249594], DEATHS_DIRGE),
    **mechanic_aliases([1249585], DISSONANCE),
    **mechanic_aliases([1286276], TERMINATE),
    **mechanic_aliases([1251789], COSMIC_FRACTURE),
    **mechanic_aliases([1254256], NAARUS_LAMENT),
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
}
