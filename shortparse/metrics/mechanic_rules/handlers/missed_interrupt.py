from shortparse.metrics.mechanic_rules.models import MechanicFailure


def get_event_source_name(event: dict) -> str:
    source = event.get("source")

    if isinstance(source, dict):
        name = source.get("name")
        if name:
            return name

    return (
        event.get("sourceName")
        or event.get("source")
        or "Unknown Caster"
    )


def analyze_missed_interrupt(
    mechanic: dict,
    event: dict,
    player_lookup: dict,
) -> MechanicFailure | None:
    if event.get("type") != "cast":
        return None

    return MechanicFailure(
        mechanic_name=mechanic["name"],
        player_name=get_event_source_name(event),
        damage=0,
    )