from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class BuildingType(str, Enum):
    GENERATOR = "generator"
    LASER = "laser"
    SHIELD = "shield"
    LAUNCHER = "launcher"


@dataclass
class Building:
    building_type: BuildingType
    hp: int = 2
    max_hp: int = 2

    @property
    def destroyed(self) -> bool:
        return self.hp <= 0

    def damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    def repair(self, amount: int = 1) -> None:
        self.hp = min(self.max_hp, self.hp + amount)


@dataclass
class Crew:
    id: str
    owner: str
    hp: int = 4
    attack: int = 2
    room_id: str = "A"
    cell_index: int = 0
    board_side: str = "self"  # self/enemy relative to owner
    alive: bool = True

    def damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.alive = False


@dataclass
class Cell:
    structure: int = 1
    max_structure: int = 1
    building: Optional[Building] = None

    @property
    def broken(self) -> bool:
        return self.structure <= 0

    def damage_structure(self, amount: int) -> None:
        self.structure = max(0, self.structure - amount)

    def repair_structure(self, amount: int = 1) -> None:
        self.structure = min(self.max_structure, self.structure + amount)


@dataclass
class Room:
    id: str
    cells: list[Cell] = field(default_factory=lambda: [Cell() for _ in range(4)])
    oxygen: int = 4
    max_oxygen: int = 4
    shield_charges: int = 0

    @property
    def abandoned(self) -> bool:
        return all(c.broken for c in self.cells)

    def tick_oxygen(self) -> None:
        if self.abandoned:
            self.oxygen = 0
            return
        broken_count = sum(1 for c in self.cells if c.broken)
        if broken_count > 0:
            self.oxygen = max(0, self.oxygen - broken_count)
        else:
            self.oxygen = min(self.max_oxygen, self.oxygen + 1)


@dataclass
class Ship:
    owner: str
    rooms: dict[str, Room]
    crews: list[Crew]

    def alive_crews(self) -> list[Crew]:
        return [c for c in self.crews if c.alive]

    def room(self, room_id: str) -> Room:
        return self.rooms[room_id]

    def generator_power(self) -> int:
        for room in self.rooms.values():
            for cell in room.cells:
                if cell.building and cell.building.building_type == BuildingType.GENERATOR and not cell.building.destroyed:
                    return 2
        return 0
