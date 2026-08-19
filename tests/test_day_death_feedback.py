from constants import ENEMY_BOAR, ENEMY_WOLF
from enemy import create_enemy
from main import (
    DEATH_REASON_BOAR,
    DEATH_REASON_COLD,
    DEATH_REASON_HUNGER,
    DEATH_REASON_WOLF,
    Game,
)


def test_new_game_has_no_death_reason_or_completed_day():
    game = Game()

    assert game.death_reason is None
    assert game.completed_day is None


def test_wolf_lethal_attack_records_wolf_reason():
    game = Game()
    wolf = create_enemy(ENEMY_WOLF, game.player)
    game.survival.health = wolf.damage

    game.enemy_attack_player(wolf)

    assert game.survival.is_dead()
    assert game.death_reason == DEATH_REASON_WOLF


def test_boar_lethal_attack_records_boar_reason():
    game = Game()
    boar = create_enemy(ENEMY_BOAR, game.player)
    game.survival.health = boar.damage

    game.enemy_attack_player(boar)

    assert game.survival.is_dead()
    assert game.death_reason == DEATH_REASON_BOAR


def test_hunger_death_records_hunger_reason():
    game = Game()
    game.phase = "day"
    game.survival.health = 3
    game.survival.hunger = 100

    result = game.apply_hunger_turn_effect()

    assert result is False
    assert game.survival.is_dead()
    assert game.phase == "game_over"
    assert game.death_reason == DEATH_REASON_HUNGER


def test_lethal_campfire_range_damage_records_cold_reason():
    game = Game()
    game.phase = "night"
    game.player = (0, 0)
    game.survival.health = 1

    game.apply_campfire_night_effects()

    assert game.survival.is_dead()
    assert game.death_reason == DEATH_REASON_COLD


def test_reset_clears_previous_death_reason():
    game = Game()
    game.death_reason = DEATH_REASON_WOLF

    game.reset()

    assert game.death_reason is None


def test_finish_night_records_completed_day_and_keeps_position():
    game = Game()
    game.day = 1
    game.phase = "night"

    original_position = (3, 3)
    game.player = original_position
    game.selected_tile = original_position

    game.finish_night()

    assert game.completed_day == 1
    assert game.day == 2
    assert game.player == original_position
    assert game.selected_tile == original_position