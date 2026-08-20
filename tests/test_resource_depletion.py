from main import Game


def test_forest_with_wood_is_not_depleted():
    game = Game()

    tile = game.player
    game.terrain[tile] = "forest"
    game.resources[tile] = 3

    assert game.resource_amount_at(tile) == 3
    assert game.is_tile_depleted(tile) is False


def test_forest_with_zero_wood_is_depleted():
    game = Game()

    tile = game.player
    game.terrain[tile] = "forest"
    game.resources[tile] = 0

    assert game.resource_amount_at(tile) == 0
    assert game.is_tile_depleted(tile) is True


def test_rock_with_zero_stone_is_depleted():
    game = Game()

    tile = game.player
    game.terrain[tile] = "rock"
    game.resources[tile] = 0

    assert game.is_tile_depleted(tile) is True


def test_grass_with_zero_food_is_depleted():
    game = Game()

    tile = game.player
    game.terrain[tile] = "grass"
    game.resources[tile] = 0

    assert game.is_tile_depleted(tile) is True


def test_water_is_not_considered_depleted_resource_tile():
    game = Game()

    tile = game.player
    game.terrain[tile] = "water"
    game.resources[tile] = 0

    assert game.resource_type_at(tile) is None
    assert game.is_tile_depleted(tile) is False


def test_gathering_last_resource_changes_tile_to_depleted():
    game = Game()

    tile = game.player
    game.terrain[tile] = "forest"
    game.resources[tile] = 1

    assert game.is_tile_depleted(tile) is False

    assert game.gather_at(tile) is True

    assert game.resources[tile] == 0
    assert game.is_tile_depleted(tile) is True