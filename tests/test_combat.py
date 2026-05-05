from src.actions import AttackTarget, CrewAction
from src.enemy_ai import plan_enemy_actions
from src.game_state import GameState
from src.resolver import execute_turn


def test_generator_provides_power_and_laser_hits_twice():
    s = GameState.initial()
    c = s.player.ship.crews[0]
    s.player.actions = [
        CrewAction(c.id, "operate_laser", move_to=("A", 1, "self"), laser_targets=[
            AttackTarget("enemy", "A", 0, "structure"),
            AttackTarget("enemy", "A", 0, "structure"),
        ])
    ]
    execute_turn(s)
    assert s.enemy.ship.room("A").cells[0].structure == 0


def test_shield_blocks_one_ranged_hit():
    s = GameState.initial()
    p = s.player.ship.crews[0]
    e = s.enemy.ship.crews[0]
    s.player.actions = [CrewAction(p.id, "operate_shield", move_to=("A", 0, "self"), shield_room="A")]
    s.enemy.actions = [CrewAction(e.id, "operate_laser", move_to=("A", 1, "self"), laser_targets=[
        AttackTarget("enemy", "A", 0, "structure"),
        AttackTarget("enemy", "A", 0, "structure"),
    ])]
    execute_turn(s)
    assert s.player.ship.room("A").cells[0].structure == 0


def test_melee_can_damage_crew_same_room():
    s = GameState.initial()
    p = s.player.ship.crews[0]
    e = s.enemy.ship.crews[0]
    p.board_side = "enemy"
    p.room_id = "A"
    p.cell_index = 2
    s.player.actions = [CrewAction(p.id, "melee", melee_target=AttackTarget("enemy", "A", 2, "crew"))]
    execute_turn(s)
    assert e.hp == 2


def test_oxygen_and_suffocation():
    s = GameState.initial()
    room = s.player.ship.room("A")
    room.cells[0].structure = 0
    room.oxygen = 1
    c = s.player.ship.crews[0]
    c.room_id = "A"
    execute_turn(s)
    assert room.oxygen == 0
    assert c.hp == 3


def test_win_condition_all_enemy_crew_dead():
    s = GameState.initial()
    for c in s.enemy.ship.crews:
        c.hp = 0
        c.alive = False
    execute_turn(s)
    assert s.winner == "player"


def test_enemy_ai_returns_intent():
    s = GameState.initial()
    plan = plan_enemy_actions(s)
    assert len(plan) >= 1
