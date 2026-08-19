from campfire import Campfire
from constants import CAMPFIRE_MAX_FUEL
from main import Game


def _fire_action(game: Game, tile):
    return next((row for row in game.context_actions(tile) if row[0] == "fire"), None)


def test_only_real_campfire_tile_has_refuel_action():
    game = Game()
    assert _fire_action(game, game.campfire.position) is not None
    other = next(tile for tile in game.terrain if tile not in game.campfires)
    assert _fire_action(game, other) is None


def test_refuel_disabled_when_far_no_wood_or_full():
    game = Game()
    tile = game.campfire.position
    game.player = (0, 0)
    assert _fire_action(game, tile)[2] is False
    game.player = tile
    game.inventory.resources["wood"] = 0
    assert _fire_action(game, tile)[2] is False
    game.inventory.resources["wood"] = 1
    game.campfire.fuel = CAMPFIRE_MAX_FUEL
    assert _fire_action(game, tile)[2] is False
    wood_before = game.inventory.get("wood")
    assert game.add_firewood_day(game.campfire) is False
    assert game.inventory.get("wood") == wood_before


def test_refueling_second_campfire_only_changes_target():
    game = Game()
    second_tile = next(tile for tile in game.terrain if tile != game.campfire.position)
    second = Campfire(second_tile)
    game.campfires[second_tile] = second
    game.player = second_tile
    primary_before = game.campfire.fuel
    second_before = second.fuel
    game.execute_context_action("fire", second_tile)
    assert second.fuel > second_before
    assert game.campfire.fuel == primary_before


def test_hud_has_no_campfire_refuel_action():
    from main import hud_buttons

    game = Game()
    actions = {action for action, _label, _rect, _enabled in hud_buttons(game)}
    assert "fire_day" not in actions
    assert "fire_night" not in actions
