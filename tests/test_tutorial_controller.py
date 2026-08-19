from main import Game
from tutorial_controller import TutorialController


def test_initial_step_is_zero():
    assert TutorialController(Game()).step == 0


def test_movement_and_resource_steps_advance():
    game = Game()
    tutorial = TutorialController(game)
    tutorial.acknowledge(game)
    game.player = next(tile for tile in game.terrain if tile != tutorial.initial_player_position)
    tutorial.update(game)
    assert tutorial.step == 2
    game.inventory.add("wood", 1)
    tutorial.update(game)
    assert tutorial.step == 3
    game.inventory.add("food", 1)
    tutorial.update(game)
    assert tutorial.step == 4
    game.inventory.add("stone", 1)
    tutorial.update(game)
    assert tutorial.step == 5


def test_tool_fire_night_and_day_two_complete():
    game = Game()
    tutorial = TutorialController(game)
    tutorial.step = 6
    game.has_pickaxe = True
    tutorial.update(game)
    assert tutorial.step == 7
    game.campfire.fuel += 1
    tutorial.update(game)
    assert tutorial.step == 8
    tutorial.acknowledge(game)
    game.phase = "night"
    tutorial.update(game)
    assert tutorial.step == 10
    game.day = 2
    game.phase = "day"
    tutorial.update(game)
    assert tutorial.completed is True
    assert tutorial.active is False
