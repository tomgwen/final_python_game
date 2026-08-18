from main import Game


def prepare_forest_tile(
    game: Game,
    wood_amount: int,
) -> tuple[int, int]:
    """把玩家目前所在格設成可控制木材數量的森林格。"""
    tile = game.player

    game.terrain[tile] = "forest"
    game.resources[tile] = wood_amount

    return tile


def test_without_axe_gathers_one_wood():
    game = Game()

    tile = prepare_forest_tile(
        game,
        wood_amount=3,
    )

    before = game.inventory.get("wood")

    assert game.has_axe is False
    assert game.gather_at(tile) is True

    assert game.inventory.get("wood") == before + 1
    assert game.resources[tile] == 2


def test_with_axe_gathers_two_wood():
    game = Game()

    tile = prepare_forest_tile(
        game,
        wood_amount=3,
    )

    game.has_axe = True

    before = game.inventory.get("wood")

    assert game.gather_at(tile) is True

    assert game.inventory.get("wood") == before + 2
    assert game.resources[tile] == 1


def test_axe_does_not_create_extra_wood_when_only_one_remains():
    game = Game()

    tile = prepare_forest_tile(
        game,
        wood_amount=1,
    )

    game.has_axe = True

    before = game.inventory.get("wood")

    assert game.gather_at(tile) is True

    assert game.inventory.get("wood") == before + 1
    assert game.resources[tile] == 0


def test_crafting_axe_enables_double_wood_gathering():
    game = Game()

    game.inventory.add("wood", 1)
    game.inventory.add("stone", 2)

    assert game.has_axe is False

    assert game.craft_axe() is True

    assert game.has_axe is True

    tile = prepare_forest_tile(
        game,
        wood_amount=3,
    )

    before = game.inventory.get("wood")

    assert game.gather_at(tile) is True

    assert game.inventory.get("wood") == before + 2
    assert game.resources[tile] == 1