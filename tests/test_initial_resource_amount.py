from main import Game


def test_all_resource_tiles_start_with_six_resources():
    game = Game()

    for tile, terrain in game.terrain.items():
        if terrain in {"grass", "forest", "rock"}:
            assert game.resources[tile] == 6


def test_water_tiles_do_not_have_gatherable_resources():
    game = Game()

    for tile, terrain in game.terrain.items():
        if terrain == "water":
            assert game.resources.get(tile, 0) == 0