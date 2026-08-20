from main import Game


def _rock_tile(game: Game) -> tuple[int, int]:
    tile = next(tile for tile, terrain in game.terrain.items() if terrain == "rock")
    game.player = tile
    game.discovered.add(tile)
    return tile


def test_new_game_does_not_have_pickaxe():
    assert Game().has_pickaxe is False


def test_crafting_pickaxe_sets_owned_state():
    game = Game()
    game.inventory.add("wood", 2)
    game.inventory.add("stone", 2)
    assert game.craft_pickaxe() is True
    assert game.has_pickaxe is True


def test_pickaxe_doubles_stone_but_not_beyond_remaining():
    game = Game()
    tile = _rock_tile(game)
    before = game.inventory.get("stone")
    game.has_pickaxe = True
    game.gather_at(tile)
    assert game.inventory.get("stone") == before + 2

    game.attack_animating = False
    game.resources[tile] = 1
    before = game.inventory.get("stone")
    game.gather_at(tile)
    assert game.inventory.get("stone") == before + 1
    assert game.resources[tile] == 0


def test_pickaxe_does_not_change_turn_cost():
    game = Game()
    tile = _rock_tile(game)
    game.has_pickaxe = True
    before = game.day_turns_left
    game.gather_at(tile)
    assert game.day_turns_left == before - 1
