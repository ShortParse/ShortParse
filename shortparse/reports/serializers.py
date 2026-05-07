from collections.abc import Mapping
from collections.abc import Sequence


def serialize_value(value):
    #
    # Primitive safe values
    #

    if value is None:
        return None

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return value

    #
    # Dictionaries
    #

    if isinstance(value, Mapping):
        return {
            str(key): serialize_value(subvalue)
            for key, subvalue in value.items()
        }

    #
    # Lists / tuples
    #

    if (
        isinstance(value, Sequence)
        and not isinstance(value, (str, bytes))
    ):
        return [
            serialize_value(item)
            for item in value
        ]

    #
    # Dataclass-like / object-like
    #

    if hasattr(value, "__dict__"):
        return serialize_value(vars(value))

    #
    # Fallback
    #

    return str(value)


def serialize_analysis(
    analysis: dict,
) -> dict:
    return serialize_value(analysis)