from main import Game


def test_day_turn_applies_hunger_effect_once():
    game = Game()
    game.phase = "day"
    game.day_turns_left = 10
    game.survival.health = 50
    game.survival.hunger = 10

    game.spend_day_turn()

    assert game.survival.health == 52
    assert game.day_turns_left == 9


def test_day_turn_high_hunger_loses_health_once():
    game = Game()
    game.phase = "day"
    game.day_turns_left = 10
    game.survival.health = 50
    game.survival.hunger = 100

    game.spend_day_turn()

    assert game.survival.health == 47
    assert game.day_turns_left == 9


def test_day_turn_hunger_death_stops_before_night():
    game = Game()
    game.phase = "day"
    game.day_turns_left = 1
    game.survival.health = 3
    game.survival.hunger = 100

    game.spend_day_turn()

    assert game.survival.health == 0
    assert game.phase == "game_over"


def test_night_turn_applies_hunger_effect_once():
    game = Game()
    game.phase = "night"
    game.night_turns_left = 10
    game.survival.health = 50
    game.survival.hunger = 10

    # 避免本測試受到火圈外環境傷害影響
    game.campfire.lit = True
    game.campfire.fuel = 10
    game.player = game.campfire.position

    game.advance_night_turn()

    assert game.survival.health >= 52