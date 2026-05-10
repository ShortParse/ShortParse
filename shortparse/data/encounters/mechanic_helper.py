def mechanic_aliases(
    spell_ids: list[int],
    mechanic: dict,
) -> dict[int, dict]:

    return {
        spell_id: {
            **mechanic,
            "spell_id": spell_id,
        }
        for spell_id in spell_ids
    }