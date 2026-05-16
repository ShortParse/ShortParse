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