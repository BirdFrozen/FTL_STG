from __future__ import annotations

from src.actions import AttackTarget, CrewAction
from src.game_state import GameState, SideState
from src.models import BuildingType, Crew, Ship


def _find_crew(side: SideState, crew_id: str) -> Crew | None:
    for c in side.ship.crews:
        if c.id == crew_id and c.alive:
            return c
    return None


def _get_ship_by_target(state: GameState, actor_side: str, target_side: str) -> Ship:
    if actor_side == "player":
        return state.player.ship if target_side == "self" else state.enemy.ship
    return state.enemy.ship if target_side == "self" else state.player.ship


def _apply_target_damage(state: GameState, actor_side: str, target: AttackTarget, damage: int, is_ranged: bool) -> None:
    ship = _get_ship_by_target(state, actor_side, target.side)
    room = ship.room(target.room_id)
    if room.abandoned:
        return
    if is_ranged and room.shield_charges > 0:
        room.shield_charges -= 1
        return
    cell = room.cells[target.cell_index]
    if target.target_type == "structure":
        cell.damage_structure(damage)
    elif target.target_type == "building" and cell.building:
        cell.building.damage(damage)
    elif target.target_type == "crew":
        for cr in ship.crews:
            if cr.alive and cr.room_id == target.room_id and cr.cell_index == target.cell_index:
                cr.damage(damage)


def execute_turn(state: GameState) -> None:
    state.player.power_available = state.player.ship.generator_power()
    state.enemy.power_available = state.enemy.ship.generator_power()

    for side_name, side in (("player", state.player), ("enemy", state.enemy)):
        for action in side.actions:
            crew = _find_crew(side, action.crew_id)
            if not crew:
                continue
            if action.move_to:
                r, c, b = action.move_to
                target_ship = side.ship if b == "self" else (state.enemy.ship if side_name == "player" else state.player.ship)
                cell = target_ship.room(r).cells[c]
                if not cell.broken and not target_ship.room(r).abandoned:
                    crew.room_id, crew.cell_index, crew.board_side = r, c, b

    for side_name, side in (("player", state.player), ("enemy", state.enemy)):
        for action in side.actions:
            crew = _find_crew(side, action.crew_id)
            if not crew:
                continue
            if action.action_type == "operate_shield" and action.shield_room and side.power_available >= 1:
                room = side.ship.room(action.shield_room)
                if crew.board_side == "self" and any(c.building and c.building.building_type == BuildingType.SHIELD and not c.building.destroyed and crew.room_id == room_id and crew.cell_index == idx for room_id, rm in side.ship.rooms.items() for idx, c in enumerate(rm.cells)):
                    side.power_available -= 1
                    room.shield_charges += 1

    for side_name, side in (("player", state.player), ("enemy", state.enemy)):
        for action in side.actions:
            crew = _find_crew(side, action.crew_id)
            if not crew:
                continue
            if action.action_type == "operate_laser" and action.laser_targets and side.power_available >= 1:
                if crew.board_side == "self":
                    side.power_available -= 1
                    for t in action.laser_targets[:2]:
                        _apply_target_damage(state, side_name, t, 1, is_ranged=True)

    melee_events: list[tuple[str, AttackTarget, int]] = []
    for side_name, side in (("player", state.player), ("enemy", state.enemy)):
        for action in side.actions:
            crew = _find_crew(side, action.crew_id)
            if crew and action.action_type == "melee" and action.melee_target:
                melee_events.append((side_name, action.melee_target, crew.attack))
    for side_name, target, dmg in melee_events:
        _apply_target_damage(state, side_name, target, dmg, is_ranged=False)

    for side_name, side in (("player", state.player), ("enemy", state.enemy)):
        for action in side.actions:
            crew = _find_crew(side, action.crew_id)
            if not crew:
                continue
            if action.action_type == "repair" and action.repair_target:
                ship = _get_ship_by_target(state, side_name, action.repair_target.side)
                if action.repair_target.side != "self":
                    continue
                room = ship.room(action.repair_target.room_id)
                if room.abandoned:
                    continue
                cell = room.cells[action.repair_target.cell_index]
                if action.repair_target.target_type == "structure":
                    cell.repair_structure(1)
                elif action.repair_target.target_type == "building" and cell.building and not cell.building.destroyed:
                    cell.building.repair(1)

    for ship in (state.player.ship, state.enemy.ship):
        for room in ship.rooms.values():
            room.tick_oxygen()
            if room.oxygen == 0:
                for c in ship.crews:
                    if c.alive and c.board_side == "self" and c.room_id == room.id:
                        c.damage(1)
            if room.abandoned:
                room.oxygen = 0
                for c in ship.crews:
                    if c.alive and c.board_side == "self" and c.room_id == room.id:
                        c.damage(999)
            for cell in room.cells:
                if cell.building and cell.building.destroyed:
                    cell.building = None

    p_dead = len(state.player.ship.alive_crews()) == 0
    e_dead = len(state.enemy.ship.alive_crews()) == 0
    p_ab = all(r.abandoned for r in state.player.ship.rooms.values())
    e_ab = all(r.abandoned for r in state.enemy.ship.rooms.values())
    if (p_dead or p_ab) and (e_dead or e_ab):
        state.winner = "enemy"
    elif e_dead or e_ab:
        state.winner = "player"
    elif p_dead or p_ab:
        state.winner = "enemy"

    state.turn += 1
    state.player.actions = []
    state.enemy.actions = []
