from constants import TOOL_MAX_DURABILITY
from main import Game


def _prepare_resource_tile(
    game: Game,
    terrain: str,
    amount: int = 100,
) -> tuple[int, int]:
    tile = game.player
    game.terrain[tile] = terrain
    game.resources[tile] = amount
    game.discovered.add(tile)
    return tile


def test_new_game_tools_have_zero_durability():
    game = Game()

    assert game.get_tool_durability("spear") == 0
    assert game.get_tool_durability("axe") == 0
    assert game.get_tool_durability("pickaxe") == 0
    assert game.get_tool_durability("bow") == 0


def test_crafting_axe_sets_full_durability():
    game = Game()
    game.inventory.add("wood", 1)
    game.inventory.add("stone", 2)

    assert game.craft_axe() is True

    assert game.has_axe is True
    assert game.get_tool_durability("axe") == TOOL_MAX_DURABILITY


def test_crafting_pickaxe_sets_full_durability():
    game = Game()
    game.inventory.add("wood", 2)
    game.inventory.add("stone", 2)

    assert game.craft_pickaxe() is True

    assert game.has_pickaxe is True
    assert game.get_tool_durability("pickaxe") == TOOL_MAX_DURABILITY


def test_crafting_spear_sets_full_durability():
    game = Game()
    game.inventory.add("wood", 2)
    game.inventory.add("stone", 1)

    assert game.craft_spear() is True

    assert game.has_spear is True
    assert game.get_tool_durability("spear") == TOOL_MAX_DURABILITY


def test_successful_axe_gather_reduces_durability():
    game = Game()
    game.set_tool_owned("axe", True)

    tile = _prepare_resource_tile(game, "forest")

    assert game.gather_at(tile) is True

    assert game.get_tool_durability("axe") == TOOL_MAX_DURABILITY - 1


def test_successful_pickaxe_gather_reduces_durability():
    game = Game()
    game.set_tool_owned("pickaxe", True)

    tile = _prepare_resource_tile(game, "rock")

    assert game.gather_at(tile) is True

    assert game.get_tool_durability("pickaxe") == TOOL_MAX_DURABILITY - 1


def test_axe_does_not_lose_durability_when_gathering_food():
    game = Game()
    game.set_tool_owned("axe", True)

    tile = _prepare_resource_tile(game, "grass")

    assert game.gather_at(tile) is True

    assert game.get_tool_durability("axe") == TOOL_MAX_DURABILITY


def test_tool_breaks_after_thirty_successful_uses():
    game = Game()
    game.set_tool_owned("axe", True)

    for _ in range(TOOL_MAX_DURABILITY):
        assert game.use_tool("axe") is True

    assert game.get_tool_durability("axe") == 0
    assert game.has_axe is False


def test_broken_tool_cannot_be_used_again():
    game = Game()
    game.set_tool_owned("axe", True)

    for _ in range(TOOL_MAX_DURABILITY):
        game.use_tool("axe")

    assert game.use_tool("axe") is False
    assert game.get_tool_durability("axe") == 0


def test_legacy_boolean_tool_state_gets_full_durability_on_first_use():
    game = Game()

    game.has_axe = True
    assert game.get_tool_durability("axe") == 0

    assert game.use_tool("axe") is True

    assert game.get_tool_durability("axe") == TOOL_MAX_DURABILITY - 1


def test_reset_removes_tools_and_durability():
    game = Game()
    game.set_tool_owned("axe", True)
    game.use_tool("axe")

    game.reset()

    assert game.has_axe is False
    assert game.get_tool_durability("axe") == 0

from enemy import create_enemy
from constants import ENEMY_WOLF

def test_spear_attack_reduces_durability_after_damage_resolution():
    game = Game()
    game.phase = "night"
    game.set_tool_owned("spear", True)

    enemy = create_enemy(ENEMY_WOLF, game.player)
    game.enemies = [enemy]

    assert game.attack_enemy_at(enemy.position) is True

    before = game.get_tool_durability("spear")

    game.finish_attack_animation()

    assert game.get_tool_durability("spear") == before - 1


def test_spear_breaks_on_final_successful_attack():
    game = Game()
    game.phase = "night"
    game.set_tool_owned("spear", True)
    game.tool_durability["spear"] = 1

    enemy = create_enemy(ENEMY_WOLF, game.player)
    game.enemies = [enemy]

    assert game.attack_enemy_at(enemy.position) is True

    game.finish_attack_animation()

    assert game.get_tool_durability("spear") == 0
    assert game.has_spear is False


def test_attack_without_spear_does_not_change_spear_durability():
    game = Game()
    game.phase = "night"

    enemy = create_enemy(ENEMY_WOLF, game.player)
    game.enemies = [enemy]

    assert game.attack_enemy_at(enemy.position) is True

    game.finish_attack_animation()

    assert game.get_tool_durability("spear") == 0