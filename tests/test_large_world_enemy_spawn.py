from constants import CAMP_POSITION
from main import Game, hex_distance


SPAWN_MIN_DISTANCE = 6
SPAWN_MAX_DISTANCE = 9


def make_all_land(game: Game) -> None:
    for tile in game.terrain:
        game.terrain[tile] = "grass"


def test_spawned_enemies_are_within_spawn_ring():
    game = Game()
    make_all_land(game)

    game.day = 1
    game.spawn_enemies()

    assert game.enemies

    for enemy in game.enemies:
        distance = hex_distance(
            enemy.position,
            CAMP_POSITION,
        )

        assert SPAWN_MIN_DISTANCE <= distance <= SPAWN_MAX_DISTANCE


def test_spawned_enemies_never_spawn_on_water():
    game = Game()

    game.day = 1
    game.spawn_enemies()

    for enemy in game.enemies:
        assert game.terrain[enemy.position] != "water"


def test_spawned_enemies_never_spawn_on_camp():
    game = Game()

    game.day = 1
    game.spawn_enemies()

    for enemy in game.enemies:
        assert enemy.position != CAMP_POSITION


def test_day_one_enemy_count_is_correct():
    game = Game()
    make_all_land(game)

    game.day = 1
    game.spawn_enemies()

    assert len(game.enemies) == 4


def test_day_two_enemy_count_is_correct():
    game = Game()
    make_all_land(game)

    game.day = 2
    game.spawn_enemies()

    assert len(game.enemies) == 6


def test_spawn_is_deterministic_for_same_day_and_world():
    game_a = Game()
    game_b = Game()

    make_all_land(game_a)
    make_all_land(game_b)

    game_a.day = 3
    game_b.day = 3

    game_a.spawn_enemies()
    game_b.spawn_enemies()

    positions_a = [
        enemy.position
        for enemy in game_a.enemies
    ]

    positions_b = [
        enemy.position
        for enemy in game_b.enemies
    ]

    assert positions_a == positions_b


def test_spawn_positions_do_not_repeat_when_candidates_are_enough():
    game = Game()
    make_all_land(game)

    game.day = 3
    game.spawn_enemies()

    positions = [
        enemy.position
        for enemy in game.enemies
    ]

    assert len(positions) == len(set(positions))