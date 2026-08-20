from constants import CAMP_POSITION, ENEMY_WOLF
from enemy import create_enemy
from main import Game, hex_distance


def make_all_land(game: Game) -> None:
    for tile in game.terrain:
        game.terrain[tile] = "grass"


def test_enemy_targets_player_when_player_is_near():
    game = Game()
    make_all_land(game)

    game.player = (8, 4)

    enemy = create_enemy(
        ENEMY_WOLF,
        (10, 4),
    )

    assert game.enemy_target(enemy) == game.player


def test_enemy_targets_camp_when_player_is_far():
    game = Game()
    make_all_land(game)

    game.player = (18, 12)

    enemy = create_enemy(
        ENEMY_WOLF,
        (10, 4),
    )

    assert game.enemy_target(enemy) == CAMP_POSITION


def test_enemy_step_reduces_distance_to_nearby_player():
    game = Game()
    make_all_land(game)

    # Disable campfire fear so this test only checks targeting.
    for campfire in game.campfires.values():
        campfire.lit = False

    game.player = (8, 4)

    enemy = create_enemy(
        ENEMY_WOLF,
        (10, 4),
    )

    before_distance = hex_distance(
        enemy.position,
        game.player,
    )

    game.enemy_step(enemy)

    after_distance = hex_distance(
        enemy.position,
        game.player,
    )

    assert after_distance < before_distance

def test_enemy_target_switches_based_on_player_distance():
    game = Game()
    make_all_land(game)

    enemy = create_enemy(
        ENEMY_WOLF,
        (10, 4),
    )

    game.player = (9, 4)
    assert game.enemy_target(enemy) == game.player

    game.player = (18, 12)
    assert game.enemy_target(enemy) == CAMP_POSITION