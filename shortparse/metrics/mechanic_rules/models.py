from dataclasses import dataclass


@dataclass
class MechanicFailure:
    mechanic_name: str
    player_name: str
    damage: int = 0