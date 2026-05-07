def normalize_name(value: str | None) -> str:
    return (
        str(value or "")
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
        .upper()
    )


TALENT_RULES = {
    # spell_id: {
    #     "classes": ["ClassName"],
    #     "specs": ["SpecName"],
    #     "required_talent_id": None,
    #     "required_talent_name": None,
    #     "notes": "Optional notes.",
    # }

    # Example:
    # 31821: {
    #     "classes": ["Paladin"],
    #     "specs": ["Holy"],
    #     "required_talent_id": None,
    #     "required_talent_name": None,
    #     "notes": "Aura Mastery is Holy Paladin only.",
    # },
}


def get_talent_rule(spell_id: int) -> dict | None:
    return TALENT_RULES.get(spell_id)


def player_matches_talent_rule(
    class_name: str,
    spec_name: str,
    rule: dict,
) -> bool:
    allowed_classes = rule.get("classes") or []
    allowed_specs = rule.get("specs") or []

    normalized_class = normalize_name(class_name)
    normalized_spec = normalize_name(spec_name)

    if allowed_classes:
        normalized_classes = {
            normalize_name(class_item)
            for class_item in allowed_classes
        }

        if normalized_class not in normalized_classes:
            return False

    if allowed_specs:
        normalized_specs = {
            normalize_name(spec_item)
            for spec_item in allowed_specs
        }

        if normalized_spec not in normalized_specs:
            return False

    return True


def player_can_access_spell(
    spell_id: int,
    class_name: str,
    spec_name: str,
    known_talent_ids: list[int] | None = None,
    known_talent_names: list[str] | None = None,
) -> bool:
    rule = get_talent_rule(spell_id)

    if not rule:
        return True

    if not player_matches_talent_rule(
        class_name,
        spec_name,
        rule,
    ):
        return False

    required_talent_id = rule.get("required_talent_id")
    required_talent_name = rule.get("required_talent_name")

    if required_talent_id:
        known_talent_ids = known_talent_ids or []

        if required_talent_id not in known_talent_ids:
            return False

    if required_talent_name:
        known_talent_names = known_talent_names or []

        normalized_known_names = {
            normalize_name(name)
            for name in known_talent_names
        }

        if normalize_name(required_talent_name) not in normalized_known_names:
            return False

    return True