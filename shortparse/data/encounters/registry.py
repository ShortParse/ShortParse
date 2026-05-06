from shortparse.data.encounters import the_voidspire
from shortparse.data.encounters import the_dreamrift
from shortparse.data.encounters import march_on_queldanas


ENCOUNTER_MODULES = [
    the_voidspire,
    the_dreamrift,
    march_on_queldanas,
]


def get_avoidable_damage(encounter_id: int) -> dict:
    for module in ENCOUNTER_MODULES:
        mechanics = module.AVOIDABLE_DAMAGE_BY_ENCOUNTER_ID.get(encounter_id)

        if mechanics:
            return mechanics

    return {}