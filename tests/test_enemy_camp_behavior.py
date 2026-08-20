from constants import CAMP_POSITION, ENEMY_WOLF
from enemy import create_enemy
from main import Game


def make_all_land(game: Game) -> None:
    for tile in game.terrain:
        game.terrain[tile] = "grass"


def test_enemy_at_camp_does_not_damage_far_player():
    game = Game()
    make_all_land(game)

    game.phase = "night"
    game.player = (18, 12)

    enemy = create_enemy(
        ENEMY_WOLF,
        CAMP_POSITION,
    )

    game.enemies = [enemy]

    health_before = game.survival.health

    game.enemy_phase()

    assert game.survival.health == health_before


def test_enemy_on_player_still_damages_player():
    game = Game()
    make_all_land(game)

    game.phase = "night"
    game.player = (8, 4)

    enemy = create_enemy(
        ENEMY_WOLF,
        game.player,
    )

    game.enemies = [enemy]

    health_before = game.survival.health

    game.enemy_phase()

    assert game.survival.health < health_before


def test_enemy_step_stops_when_already_at_target():
    game = Game()
    make_all_land(game)

    game.player = (18, 12)

    enemy = create_enemy(
        ENEMY_WOLF,
        CAMP_POSITION,
    )

    before = enemy.position

    result = game.enemy_step(enemy)

    assert result is False
    assert enemy.position == before