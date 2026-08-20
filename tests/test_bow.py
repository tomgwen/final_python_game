from constants import (
    RESOURCE_ARROW,
    TOOL_MAX_DURABILITY,
)
from main import Game


def test_new_game_starts_with_zero_arrows():
    game = Game()

    assert game.inventory.get(RESOURCE_ARROW) == 0


def test_arrow_is_valid_inventory_resource():
    game = Game()

    game.inventory.add(RESOURCE_ARROW, 3)

    assert game.inventory.get(RESOURCE_ARROW) == 3


def test_craft_bow_creates_bow_with_full_durability():
    game = Game()

    game.inventory.add("hide", 1)

    assert game.craft_bow() is True
    assert game.has_bow is True
    assert game.get_tool_durability("bow") == TOOL_MAX_DURABILITY


def test_craft_bow_spends_resources():
    game = Game()

    game.inventory.add("hide", 1)

    wood_before = game.inventory.get("wood")
    hide_before = game.inventory.get("hide")

    assert game.craft_bow() is True

    assert game.inventory.get("wood") == wood_before - 2
    assert game.inventory.get("hide") == hide_before - 1


def test_cannot_craft_second_bow_while_owned():
    game = Game()

    game.inventory.add("hide", 2)

    assert game.craft_bow() is True

    wood_after_first = game.inventory.get("wood")
    hide_after_first = game.inventory.get("hide")

    assert game.craft_bow() is False

    assert game.inventory.get("wood") == wood_after_first
    assert game.inventory.get("hide") == hide_after_first


def test_cannot_craft_bow_without_hide():
    game = Game()

    assert game.inventory.get("hide") == 0
    assert game.craft_bow() is False
    assert game.has_bow is False


def test_craft_arrows_adds_five_arrows():
    game = Game()

    assert game.craft_arrows() is True

    assert game.inventory.get(RESOURCE_ARROW) == 5


def test_craft_arrows_spends_one_wood_and_one_stone():
    game = Game()

    wood_before = game.inventory.get("wood")
    stone_before = game.inventory.get("stone")

    assert game.craft_arrows() is True

    assert game.inventory.get("wood") == wood_before - 1
    assert game.inventory.get("stone") == stone_before - 1


def test_cannot_craft_arrows_without_materials():
    game = Game()

    game.inventory.resources["wood"] = 0
    game.inventory.resources["stone"] = 0

    assert game.craft_arrows() is False
    assert game.inventory.get(RESOURCE_ARROW) == 0


def test_bow_cannot_be_crafted_at_night():
    game = Game()
    game.phase = "night"
    game.inventory.add("hide", 1)

    assert game.craft_bow() is False


def test_arrows_cannot_be_crafted_at_night():
    game = Game()
    game.phase = "night"

    assert game.craft_arrows() is False
from constants import ENEMY_WOLF
from enemy import create_enemy
from main import hex_distance


def find_tile_at_distance(game: Game, origin, distance: int):
    return next(
        tile
        for tile in game.terrain
        if hex_distance(origin, tile) == distance
    )


def prepare_bow(game: Game, arrows: int = 5):
    game.set_tool_owned("bow", True)
    game.inventory.add(RESOURCE_ARROW, arrows)


def test_bow_can_attack_enemy_three_tiles_away():
    game = Game()
    game.phase = "night"
    prepare_bow(game)

    target = find_tile_at_distance(game, game.player, 3)
    enemy = create_enemy(ENEMY_WOLF, target)
    game.enemies = [enemy]

    assert game.attack_enemy_at(target) is True
    assert game.attack_weapon == "bow"


def test_bow_attack_deals_fifteen_damage():
    game = Game()
    game.phase = "night"
    prepare_bow(game)

    # 關閉所有營火，避免夜晚回合的營火傷害干擾弓箭傷害測試。
    for campfire in game.campfires.values():
        campfire.lit = False
        campfire.fuel = 0

    target = find_tile_at_distance(game, game.player, 3)
    enemy = create_enemy(ENEMY_WOLF, target)
    game.enemies = [enemy]

    assert game.attack_enemy_at(target) is True

    health_before = enemy.health
    game.finish_attack_animation()

    assert enemy.health == health_before - 15


def test_bow_attack_consumes_one_arrow():
    game = Game()
    game.phase = "night"
    prepare_bow(game, arrows=5)

    target = find_tile_at_distance(game, game.player, 3)
    enemy = create_enemy(ENEMY_WOLF, target)
    game.enemies = [enemy]

    assert game.attack_enemy_at(target) is True

    game.finish_attack_animation()

    assert game.inventory.get(RESOURCE_ARROW) == 4


def test_bow_attack_reduces_bow_durability():
    game = Game()
    game.phase = "night"
    prepare_bow(game)

    target = find_tile_at_distance(game, game.player, 3)
    enemy = create_enemy(ENEMY_WOLF, target)
    game.enemies = [enemy]

    before = game.get_tool_durability("bow")

    assert game.attack_enemy_at(target) is True
    game.finish_attack_animation()

    assert game.get_tool_durability("bow") == before - 1


def test_bow_breaks_after_final_shot():
    game = Game()
    game.phase = "night"
    prepare_bow(game)

    game.tool_durability["bow"] = 1

    target = find_tile_at_distance(game, game.player, 3)
    enemy = create_enemy(ENEMY_WOLF, target)
    game.enemies = [enemy]

    assert game.attack_enemy_at(target) is True

    game.finish_attack_animation()

    assert game.has_bow is False
    assert game.get_tool_durability("bow") == 0


def test_cannot_attack_at_range_three_without_arrow():
    game = Game()
    game.phase = "night"
    game.set_tool_owned("bow", True)

    target = find_tile_at_distance(game, game.player, 3)
    enemy = create_enemy(ENEMY_WOLF, target)
    game.enemies = [enemy]

    assert game.inventory.get(RESOURCE_ARROW) == 0
    assert game.attack_enemy_at(target) is False


def test_cannot_attack_at_range_three_without_bow():
    game = Game()
    game.phase = "night"
    game.inventory.add(RESOURCE_ARROW, 5)

    target = find_tile_at_distance(game, game.player, 3)
    enemy = create_enemy(ENEMY_WOLF, target)
    game.enemies = [enemy]

    assert game.attack_enemy_at(target) is False


def test_spear_is_preferred_at_range_two():
    game = Game()
    game.phase = "night"
    game.set_tool_owned("spear", True)
    prepare_bow(game)

    target = find_tile_at_distance(game, game.player, 2)
    enemy = create_enemy(ENEMY_WOLF, target)
    game.enemies = [enemy]

    arrows_before = game.inventory.get(RESOURCE_ARROW)
    bow_before = game.get_tool_durability("bow")
    spear_before = game.get_tool_durability("spear")

    assert game.attack_enemy_at(target) is True
    assert game.attack_weapon == "spear"

    game.finish_attack_animation()

    assert game.inventory.get(RESOURCE_ARROW) == arrows_before
    assert game.get_tool_durability("bow") == bow_before
    assert game.get_tool_durability("spear") == spear_before - 1


def test_bow_is_used_at_range_two_without_spear():
    game = Game()
    game.phase = "night"
    prepare_bow(game)

    target = find_tile_at_distance(game, game.player, 2)
    enemy = create_enemy(ENEMY_WOLF, target)
    game.enemies = [enemy]

    assert game.attack_enemy_at(target) is True
    assert game.attack_weapon == "bow"


def test_close_enemy_does_not_waste_arrow():
    game = Game()
    game.phase = "night"
    prepare_bow(game)

    target = find_tile_at_distance(game, game.player, 1)
    enemy = create_enemy(ENEMY_WOLF, target)
    game.enemies = [enemy]

    arrows_before = game.inventory.get(RESOURCE_ARROW)
    bow_before = game.get_tool_durability("bow")

    assert game.attack_enemy_at(target) is True
    assert game.attack_weapon == "unarmed"

    game.finish_attack_animation()

    assert game.inventory.get(RESOURCE_ARROW) == arrows_before
    assert game.get_tool_durability("bow") == bow_before
def test_bow_and_arrow_recipes_exist():
    from recipe_catalog import get_recipe

    bow = get_recipe("bow")
    arrows = get_recipe("arrows")

    assert bow is not None
    assert arrows is not None

    assert bow["cost"] == {
        "wood": 2,
        "hide": 1,
    }

    assert arrows["cost"] == {
        "wood": 1,
        "stone": 1,
    }