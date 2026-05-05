from __future__ import annotations

from src.actions import AttackTarget, CrewAction
from src.game_state import GameState


def plan_enemy_actions(state: GameState) -> list[CrewAction]:
    actions: list[CrewAction] = []
    enemy_crews = [c for c in state.enemy.ship.crews if c.alive and c.board_side == "self"]
    for c in enemy_crews:
        if c.room_id == "A" and c.cell_index == 2:
            actions.append(
                CrewAction(
                    crew_id=c.id,
                    action_type="operate_laser",
                    move_to=("A", 1, "self"),
                    laser_targets=[
                        AttackTarget("enemy", "A", 1, "building"),
                        AttackTarget("enemy", "A", 2, "crew"),
                    ],
                )
            )
        else:
            actions.append(CrewAction(crew_id=c.id, action_type="operate_shield", move_to=("A", 0, "self"), shield_room="B"))
    return actions
