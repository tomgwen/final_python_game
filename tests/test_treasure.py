import random

from main import Game
from treasure import TreasureChest, generate_chest_contents


def test_generate_chest_contents_has_two_to_four_resource_types():
    contents = generate_chest_contents(random.Random(123))

    assert 2 <= len(contents) <= 4


def test_generated_chest_contents_are_positive():
    contents = generate_chest_contents(random.Random(123))

    assert contents
    assert all(amount > 0 for amount in contents.values())


def test_generated_chest_contents_only_use_known_resources():
    contents = generate_chest_contents(random.Random(123))

    assert set(contents).issubset(
        {"food", "wood", "stone", "hide", "arrow"}
    )


def test_game_generates_six_treasure_chests():
    game = Game()

    assert len(game.treasure_chests) == 6


def test_treasure_chests_do_not_spawn_on_water():
    game = Game()

    for tile in game.treasure_chests:
        assert game.terrain[tile] != "water"


def test_treasure_chests_do_not_spawn_on_primary_campfire():
    game = Game()

    assert game.campfire.position not in game.treasure_chests


def test_treasure_chest_at_returns_matching_chest():
    game = Game()

    tile, chest = next(iter(game.treasure_chests.items()))

    assert game.treasure_chest_at(tile) is chest


def test_player_can_open_adjacent_treasure_chest():
    game = Game()

    tile, chest = next(iter(game.treasure_chests.items()))

    game.player = tile

    inventory_before = {
        resource: game.inventory.get(resource)
        for resource in chest.contents
    }

    assert game.open_treasure_chest(chest) is True
    assert chest.opened is True

    for resource, amount in chest.contents.items():
        assert game.inventory.get(resource) == inventory_before[resource] + amount


def test_opened_treasure_chest_cannot_be_opened_twice():
    game = Game()

    tile, chest = next(iter(game.treasure_chests.items()))
    game.player = tile

    assert game.open_treasure_chest(chest) is True

    inventory_after_first_open = {
        resource: game.inventory.get(resource)
        for resource in chest.contents
    }

    assert game.open_treasure_chest(chest) is False

    for resource in chest.contents:
        assert game.inventory.get(resource) == inventory_after_first_open[resource]


def test_player_cannot_open_far_treasure_chest():
    game = Game()

    tile, chest = next(iter(game.treasure_chests.items()))

    far_tile = next(
        candidate
        for candidate in game.terrain
        if __import__("main").hex_distance(candidate, tile) > 1
    )

    game.player = far_tile

    assert game.open_treasure_chest(chest) is False
    assert chest.opened is False


def test_chest_contents_are_deterministic_with_same_seed():
    rng1 = random.Random(42)
    rng2 = random.Random(42)

    assert generate_chest_contents(rng1) == generate_chest_contents(rng2)
def _treasure_action(game: Game, tile):
    return next(
        (
            action
            for action in game.context_actions(tile)
            if action[0] == "treasure"
        ),
        None,
    )


def test_unopened_chest_has_context_action():
    game = Game()

    tile, chest = next(iter(game.treasure_chests.items()))
    game.player = tile

    action = _treasure_action(game, tile)

    assert action is not None
    assert action[0] == "treasure"
    assert action[1] == "打開寶箱"
    assert action[2] is True


def test_far_chest_context_action_is_disabled():
    game = Game()

    tile, chest = next(iter(game.treasure_chests.items()))

    game.player = next(
        candidate
        for candidate in game.terrain
        if __import__("main").hex_distance(candidate, tile) > 1
    )

    action = _treasure_action(game, tile)

    assert action is not None
    assert action[2] is False


def test_context_action_opens_chest():
    game = Game()

    tile, chest = next(iter(game.treasure_chests.items()))
    game.player = tile

    game.execute_context_action("treasure", tile)

    assert chest.opened is True


def test_opened_chest_context_action_is_disabled():
    game = Game()

    tile, chest = next(iter(game.treasure_chests.items()))
    game.player = tile

    assert game.open_treasure_chest(chest) is True

    action = _treasure_action(game, tile)

    assert action is not None
    assert action[1] == "寶箱已開啟"
    assert action[2] is False


def test_treasure_can_be_opened_at_night():
    game = Game()

    tile, chest = next(iter(game.treasure_chests.items()))
    game.player = tile
    game.phase = "night"

    action = _treasure_action(game, tile)

    assert action is not None
    assert action[2] is True


def test_treasure_action_disabled_during_attack_animation():
    game = Game()

    tile, chest = next(iter(game.treasure_chests.items()))
    game.player = tile
    game.phase = "night"
    game.attack_animating = True

    action = _treasure_action(game, tile)

    assert action is not None
    assert action[2] is False
def test_generated_chest_never_has_more_than_four_reward_types():
    for seed in range(50):
        contents = generate_chest_contents(random.Random(seed))

        assert 2 <= len(contents) <= 4