from __future__ import annotations

from dataclasses import dataclass, field

from src.actions import CrewAction
from src.models import Building, BuildingType, Crew, Room, Ship


@dataclass
class SideState:
    ship: Ship
    power_available: int = 0
    actions: list[CrewAction] = field(default_factory=list)


@dataclass
class GameState:
    player: SideState
    enemy: SideState
    turn: int = 1
    winner: str | None = None

    @staticmethod
    def initial() -> "GameState":
        def mk_ship(owner: str) -> Ship:
            ra = Room("A")
            rb = Room("B")
            ra.cells[0].building = Building(BuildingType.SHIELD)
            ra.cells[1].building = Building(BuildingType.LASER)
            rb.cells[0].building = Building(BuildingType.GENERATOR)
            rb.cells[1].building = Building(BuildingType.LAUNCHER)
            crews = [
                Crew(id=f"{owner}_c1", owner=owner, room_id="A", cell_index=2, board_side="self"),
                Crew(id=f"{owner}_c2", owner=owner, room_id="B", cell_index=2, board_side="self"),
            ]
            return Ship(owner=owner, rooms={"A": ra, "B": rb}, crews=crews)

        return GameState(player=SideState(mk_ship("player")), enemy=SideState(mk_ship("enemy")))
