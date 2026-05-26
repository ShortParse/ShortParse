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


ENCOUNTER_ID = 3180
ENCOUNTER_NAME = "Lightblinded Vanguard"

# ============================================================
# Lightblinded Vanguard
# ============================================================

AVENGERS_SHIELD: Mechanic = {
    "name": "Avenger's Shield",
    "severity": "Major",
    "avoidable": True,
    "category": "spread",
    "failure_type": "spread_failure",
    "counts_as_failure": True,
    "max_reasonable_hits": 4,
    "score_per_hit": 50,
    "applies_to": ALL_ROLES,
    "spell_ids": [1246502],
    "note": (
        "Players targeted by Avenger's Shield explode and splash nearby players."
    ),
    "recommendation": (
        "Spread out and avoid standing inside another player's Avenger's Shield circle."
    ),
    "wcl_type": "damage_taken",
}

EXECUTION_SENTENCE: Mechanic = {
    "name": "Execution Sentence",
    "severity": "Critical",
    "avoidable": False,
    "category": "stack",
    "failure_type": "multi_soak",
    "counts_as_failure": False,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "spell_ids": [1249024],
    "note": (
        "Execution Sentence damage is split between nearby players. "
        "Players should soak one circle only."
    ),
    "recommendation": (
        "Help soak one Execution Sentence circle and avoid overlapping multiple circles."
    ),
    "wcl_type": "damage_taken",
}

DIVINE_STORM: Mechanic = {
    "name": "Divine Storm",
    "severity": "Info",
    "avoidable": True,
    "category": "boss_range",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 3,
    "score_per_hit": 10,
    "applies_to": ALL_ROLES,
    "spell_ids": [1246765],
    "note": (
        "Lightblood spins and damages players standing near him."
    ),
    "recommendation": (
        "Move away from Lightblood during Divine Storm."
    ),
    "wcl_type": "damage_taken",
}

DIVINE_HAMMER: Mechanic = {
    "name": "Divine Hammer",
    "severity": "Major",
    "avoidable": True,
    "category": "lane_movement",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 40,
    "applies_to": ALL_ROLES,
    "spell_ids": [1249047],
    "note": (
        "Holy hammers spiral outward from Execution Sentence impact zones."
    ),
    "recommendation": (
        "Move between the rotating hammers and avoid their path."
    ),
    "wcl_type": "damage_taken",
}

DIVINE_TOLL: Mechanic = {
    "name": "Divine Toll",
    "severity": "Major",
    "avoidable": True,
    "category": "traveling_projectile",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 45,
    "applies_to": ALL_ROLES,
    "spell_ids": [1248652],
    "note": (
        "Traveling holy shields move across the platform and silence players hit."
    ),
    "recommendation": (
        "Dodge incoming Divine Toll shields."
    ),
    "wcl_type": "damage_taken",
}

DIVINE_CONSECRATION: Mechanic = {
    "name": "Divine Consecration",
    "severity": "Critical",
    "avoidable": True,
    "category": "ground_effect",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 75,
    "applies_to": ALL_ROLES,
    "spell_ids": [1276982],
    "note": (
        "Consecrated ground damages, pacifies, and increases damage taken."
    ),
    "recommendation": (
        "Move out of Divine Consecration immediately."
    ),
    "wcl_type": "damage_taken",
}

TRAMPLED: Mechanic = {
    "name": "Trampled",
    "severity": "Major",
    "avoidable": True,
    "category": "frontal",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 50,
    "applies_to": ALL_ROLES,
    "spell_ids": [1249135],
    "note": (
        "Senn charges forward on her elekk, damaging players in her path."
    ),
    "recommendation": (
        "Move out of the Elekk charge path."
    ),
    "wcl_type": "damage_taken",
}

BLINDING_LIGHT: Mechanic = {
    "name": "Blinding Light",
    "severity": "Major",
    "avoidable": True,
    "category": "interrupt",
    "failure_type": "missed_interrupt",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 60,
    "applies_to": ALL_ROLES,
    "spell_ids": [1258514],
    "note": (
        "Senn emits a disorienting flash of holy light."
    ),
    "recommendation": (
        "Interrupt or avoid facing Senn during Blinding Light."
    ),
    "wcl_type": "damage_taken",
}

JUDGMENT: Mechanic = {
    "name": "Judgment",
    "severity": "Critical",
    "avoidable": False,
    "category": "tank_buster",
    "failure_type": "tank_failure",
    "counts_as_failure": False,
    "max_reasonable_hits": 2,
    "score_per_hit": 50,
    "applies_to": TANK_ONLY,
    "spell_ids": [1251857, 1246736],
    "note": (
        "Judgment increases damage taken from the follow-up tank strike."
    ),
    "recommendation": (
        "Tank swap immediately after Judgment."
    ),
    "wcl_type": "damage_taken",
}

FINAL_VERDICT: Mechanic = {
    "name": "Final Verdict",
    "severity": "Critical",
    "avoidable": False,
    "category": "tank_buster",
    "failure_type": "tank_failure",
    "counts_as_failure": False,
    "max_reasonable_hits": 1,
    "score_per_hit": 60,
    "applies_to": TANK_ONLY,
    "spell_ids": [1251812],
    "note": (
        "Heavy follow-up tank strike after Judgment."
    ),
    "recommendation": (
        "Use defensives and ensure proper tank swaps."
    ),
    "wcl_type": "damage_taken",
}

SHIELD_OF_THE_RIGHTEOUS: Mechanic = {
    "name": "Shield of the Righteous",
    "severity": "Critical",
    "avoidable": False,
    "category": "tank_buster",
    "failure_type": "tank_failure",
    "counts_as_failure": False,
    "max_reasonable_hits": 1,
    "score_per_hit": 60,
    "applies_to": TANK_ONLY,
    "spell_ids": [1251859],
    "note": (
        "Heavy follow-up tank strike after Judgment."
    ),
    "recommendation": (
        "Use defensives and ensure proper tank swaps."
    ),
    "wcl_type": "damage_taken",
}

EXORCISM: Mechanic = {
    "name": "Exorcism",
    "severity": "Major",
    "avoidable": False,
    "category": "tank_buster",
    "failure_type": "tank_failure",
    "counts_as_failure": False,
    "max_reasonable_hits": 3,
    "score_per_hit": 30,
    "applies_to": TANK_ONLY,
    "spell_ids": [1246745],
    "note": (
        "Heavy Holy damage strike against the current tank."
    ),
    "recommendation": (
        "Use defensives for Exorcism."
    ),
    "wcl_type": "damage_taken",
}

AVOIDABLE_DAMAGE = {
    **mechanic_aliases([1246502], AVENGERS_SHIELD),
    **mechanic_aliases([1249024], EXECUTION_SENTENCE),
    **mechanic_aliases([1246765], DIVINE_STORM),
    **mechanic_aliases([1249047], DIVINE_HAMMER),
    **mechanic_aliases([1248652], DIVINE_TOLL),
    **mechanic_aliases([1276982], DIVINE_CONSECRATION),
    **mechanic_aliases([1249135], TRAMPLED),
    **mechanic_aliases([1258514], BLINDING_LIGHT),
    **mechanic_aliases([1251857, 1246736], JUDGMENT),
    **mechanic_aliases([1251812], FINAL_VERDICT),
    **mechanic_aliases([1251859], SHIELD_OF_THE_RIGHTEOUS),
    **mechanic_aliases([1246745], EXORCISM),
}