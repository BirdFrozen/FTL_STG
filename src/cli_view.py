from __future__ import annotations

from src.actions import AttackTarget, CrewAction
from src.game_state import GameState


def print_state(state: GameState) -> None:
    print(f"\n=== Turn {state.turn} ===")
    for label, side in (("Player", state.player.ship), ("Enemy", state.enemy.ship)):
        print(f"[{label}]")
        for rid, room in side.rooms.items():
            print(f"  Room {rid}: oxygen={room.oxygen} abandoned={room.abandoned}")
            for i, cell in enumerate(room.cells):
                b = cell.building.building_type.value if cell.building else "-"
                print(f"    {rid}{i+1}: struct={cell.structure}, build={b}")
        crews = [f"{c.id} hp={c.hp} at {c.board_side}:{c.room_id}{c.cell_index+1}" for c in side.crews if c.alive]
        print("  crews:", ", ".join(crews) if crews else "none")


def ask_player_actions(state: GameState) -> list[CrewAction]:
    actions: list[CrewAction] = []
    print("输入每个船员行动：wait / melee / laser / shield")
    for c in state.player.ship.alive_crews():
        cmd = input(f"{c.id}> ").strip().lower()
        if cmd == "laser":
            actions.append(CrewAction(c.id, "operate_laser", laser_targets=[AttackTarget("enemy", "A", 0, "structure"), AttackTarget("enemy", "B", 0, "structure")]))
        elif cmd == "shield":
            actions.append(CrewAction(c.id, "operate_shield", shield_room="A"))
        elif cmd == "melee":
            actions.append(CrewAction(c.id, "melee", melee_target=AttackTarget("enemy", c.room_id, c.cell_index, "crew")))
        else:
            actions.append(CrewAction(c.id, "wait"))
    return actions
