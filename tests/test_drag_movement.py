from constants import (
    CAMP_POSITION,
    ENEMY_BOAR,
    MAP_COLS,
    MAP_ROWS,
)
from enemy import create_enemy
from main import DAY_TURNS, NIGHT_TURNS, Game


def make_open_map(game: Game) -> None:
    for r in range(MAP_ROWS):
        for q in range(MAP_COLS):
            game.terrain[(q, r)] = "grass"


def test_day_drag_three_hex_edges_costs_three_turns():
    game = Game()
    make_open_map(game)

    target = (8, 4)
    path = game.preview_drag_path(target)

    assert path is not None
    assert len(path) - 1 == 3

    assert game.execute_drag_path(path) is True
    assert game.player == target
    assert game.day_turns_left == DAY_TURNS - 3


def test_day_drag_rejects_path_when_turns_are_insufficient():
    game = Game()
    make_open_map(game)

    game.day_turns_left = 2

    start = game.player
    path = game.preview_drag_path((8, 4))

    assert path is not None
    assert len(path) - 1 == 3

    assert game.execute_drag_path(path) is False
    assert game.player == start
    assert game.day_turns_left == 2


def test_drag_path_avoids_water():
    game = Game()
    make_open_map(game)

    game.terrain[(6, 4)] = "water"

    path = game.preview_drag_path((7, 4))

    assert path is not None
    assert (6, 4) not in path


def test_night_drag_costs_one_turn_and_enemy_phase_per_step():
    game = Game()
    make_open_map(game)

    game.phase = "night"
    game.night_turns_left = NIGHT_TURNS

    # Keep one living enemy in the game so the normal night-complete
    # check does not immediately finish the night.
    game.enemies = [
        create_enemy(
            ENEMY_BOAR,
            (10, 7),
        )
    ]

    enemy_phase_calls = 0

    def fake_enemy_phase():
        nonlocal enemy_phase_calls
        enemy_phase_calls += 1

    game.enemy_phase = fake_enemy_phase

    path = game.preview_drag_path((8, 4))

    assert path is not None
    assert len(path) - 1 == 3

    assert game.execute_drag_path(path) is True

    assert game.player == (8, 4)
    assert game.night_turns_left == NIGHT_TURNS - 3
    assert enemy_phase_calls == 3


def test_night_preview_avoids_enemy_tile():
    game = Game()
    make_open_map(game)

    game.phase = "night"
    game.night_turns_left = NIGHT_TURNS

    enemy = create_enemy(
        ENEMY_BOAR,
        (6, 4),
    )
    game.enemies = [enemy]

    path = game.preview_drag_path((7, 4))

    assert path is not None
    assert (6, 4) not in path