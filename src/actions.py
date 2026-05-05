from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

TargetType = Literal["crew", "building", "structure"]


@dataclass
class AttackTarget:
    side: str
    room_id: str
    cell_index: int
    target_type: TargetType


@dataclass
class CrewAction:
    crew_id: str
    action_type: Literal["wait", "melee", "repair", "operate_laser", "operate_shield", "operate_launcher"]
    move_to: Optional[tuple[str, int, str]] = None
    # (room_id, cell_index, board_side)
    melee_target: Optional[AttackTarget] = None
    repair_target: Optional[AttackTarget] = None
    laser_targets: Optional[list[AttackTarget]] = None
    shield_room: Optional[str] = None
    launch_target: Optional[tuple[str, int]] = None
