from main import Game


def get_resource_tile(game: Game) -> tuple[int, int]:
    for tile, terrain in game.terrain.items():
        if terrain in {"grass", "forest", "rock"}:
            return tile
    raise AssertionError("No resource tile found")


def test_depleted_resource_records_depletion_day():
    game = Game()
    tile = get_resource_tile(game)

    game.player = tile
    game.selected_tile = tile
    game.phase = "day"
    game.resources[tile] = 1

    assert game.gather_at(tile) is True

    assert game.resources[tile] == 0
    assert game.resource_depleted_day[tile] == game.day


def test_resource_does_not_regenerate_after_only_one_day():
    game = Game()
    tile = get_resource_tile(game)

    game.resources[tile] = 0
    game.resource_depleted_day[tile] = 1

    game.day = 2
    game.regenerate_resources()

    assert game.resources[tile] == 0
    assert tile in game.resource_depleted_day


def test_resource_regenerates_after_two_days():
    game = Game()
    tile = get_resource_tile(game)

    game.resources[tile] = 0
    game.resource_depleted_day[tile] = 1

    game.day = 3
    game.regenerate_resources()

    assert game.resources[tile] == 6
    assert tile not in game.resource_depleted_day


def test_non_depleted_resource_is_not_changed():
    game = Game()
    tile = get_resource_tile(game)

    game.resources[tile] = 4
    game.day = 10

    game.regenerate_resources()

    assert game.resources[tile] == 4