from typing import Literal
from typing import TypedDict
from typing import TypeAlias

MechanicCategory: TypeAlias = Literal[
    "ground_effect",
    "swirl",
    "traveling_projectile",
    "beam",
    "frontal",
    "rear_cone",
    "forced_movement",
    "interrupt",
    "minimum_soak",
    "soak_participation",
    "bad_soak",
    "dispel",
    "spread",
    "stack",
    "boss_threat",
    "boss_range",
    "tank_buster",
    "tank_positioning",
    "add_management",
    "add_priority",
    "corpse_explosion",
    "bait",
    "lane_movement",
    "debuff_damage",
]


MechanicFailureType: TypeAlias = Literal[
    "avoidable_damage",
    "missed_interrupt",
    "minimum_soak",
    "zero_participation",
    "bad_soak",
    "missed_dispel",
    "bad_dispel",
    "spread_failure",
    "stack_failure",
    "boss_range",
]


CATEGORY_GROUND_EFFECT: MechanicCategory = "ground_effect"
CATEGORY_SWIRL: MechanicCategory = "swirl"
CATEGORY_TRAVELING_PROJECTILE: MechanicCategory = "traveling_projectile"
CATEGORY_BEAM: MechanicCategory = "beam"
CATEGORY_FRONTAL: MechanicCategory = "frontal"
CATEGORY_REAR_CONE: MechanicCategory = "rear_cone"
CATEGORY_FORCED_MOVEMENT: MechanicCategory = "forced_movement"
CATEGORY_INTERRUPT: MechanicCategory = "interrupt"
CATEGORY_MINIMUM_SOAK: MechanicCategory = "minimum_soak"
CATEGORY_SOAK_PARTICIPATION: MechanicCategory = "soak_participation"
CATEGORY_BAD_SOAK: MechanicCategory = "bad_soak"
CATEGORY_DISPEL: MechanicCategory = "dispel"
CATEGORY_SPREAD: MechanicCategory = "spread"
CATEGORY_STACK: MechanicCategory = "stack"
CATEGORY_BOSS_THREAT: MechanicCategory = "boss_threat"
CATEGORY_BOSS_RANGE: MechanicCategory = "boss_range"
CATEGORY_TANK_BUSTER: MechanicCategory = "tank_buster"
CATEGORY_TANK_POSITIONING: MechanicCategory = "tank_positioning"
CATEGORY_ADD_MANAGEMENT: MechanicCategory = "add_management"
CATEGORY_ADD_PRIORITY: MechanicCategory = "add_priority"
CATEGORY_CORPSE_EXPLOSION: MechanicCategory = "corpse_explosion"
CATEGORY_BAIT: MechanicCategory = "bait"
CATEGORY_LANE_MOVEMENT: MechanicCategory = "lane_movement"
CATEGORY_DEBUFF_DAMAGE: MechanicCategory = "debuff_damage"


FAILURE_AVOIDABLE_DAMAGE: MechanicFailureType = "avoidable_damage"
FAILURE_MISSED_INTERRUPT: MechanicFailureType = "missed_interrupt"
FAILURE_MINIMUM_SOAK: MechanicFailureType = "minimum_soak"
FAILURE_ZERO_PARTICIPATION: MechanicFailureType = "zero_participation"
FAILURE_BAD_SOAK: MechanicFailureType = "bad_soak"
FAILURE_MISSED_DISPEL: MechanicFailureType = "missed_dispel"
FAILURE_BAD_DISPEL: MechanicFailureType = "bad_dispel"
FAILURE_SPREAD_FAILURE: MechanicFailureType = "spread_failure"
FAILURE_STACK_FAILURE: MechanicFailureType = "stack_failure"
FAILURE_BOSS_RANGE: MechanicFailureType = "boss_range"

class Mechanic(TypedDict, total=False):
    name: str

    severity: str
    avoidable: bool

    category: MechanicCategory
    failure_type: MechanicFailureType

    counts_as_failure: bool

    max_reasonable_hits: int
    score_per_hit: int

    applies_to: list[str]

    note: str
    recommendation: str

    wcl_type: str

    spell_ids: list[int]
    minimum_soakers: int
    mrt: bool