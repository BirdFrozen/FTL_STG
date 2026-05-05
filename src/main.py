from src.cli_view import ask_player_actions, print_state
from src.enemy_ai import plan_enemy_actions
from src.game_state import GameState
from src.resolver import execute_turn


def main() -> None:
    state = GameState.initial()
    while not state.winner:
        print_state(state)
        enemy_plan = plan_enemy_actions(state)
        print("Enemy intent:", [a.action_type for a in enemy_plan])
        state.enemy.actions = enemy_plan
        state.player.actions = ask_player_actions(state)
        execute_turn(state)
    print_state(state)
    print("Winner:", state.winner)


if __name__ == "__main__":
    main()
