"""Tests for the Crafting system."""

from crafting import Equipment, craft, get_recipe
from inventory import Inventory


def test_stone_spear_craft() -> None:
    """Crafting a stone spear consumes the correct resources."""
    inventory = Inventory()
    equipment = Equipment()

    result = craft("stone_spear", inventory, equipment)

    assert result is True
    assert equipment.has_stone_spear is True
    assert inventory.get("wood") == 3
    assert inventory.get("stone") == 1


def test_stone_axe_craft() -> None:
    """Crafting a stone axe consumes the correct resources."""
    inventory = Inventory()
    equipment = Equipment()

    result = craft("stone_axe", inventory, equipment)

    assert result is True
    assert equipment.has_stone_axe is True
    assert inventory.get("wood") == 4
    assert inventory.get("stone") == 0


def test_torch_craft() -> None:
    """Crafting a torch consumes one wood."""
    inventory = Inventory()
    equipment = Equipment()

    result = craft("torch", inventory, equipment)

    assert result is True
    assert equipment.has_torch is True
    assert inventory.get("wood") == 4


def test_hide_armor_craft() -> None:
    """Hide armor can be crafted without modifying SurvivalStats."""
    inventory = Inventory()
    inventory.add("hide", 2)
    equipment = Equipment()

    result = craft("hide_armor", inventory, equipment)

    assert result is True
    assert inventory.get("hide") == 0
    assert inventory.get("stone") == 1


def test_hide_armor_can_be_crafted_again() -> None:
    """Hide armor is allowed to be crafted repeatedly."""
    inventory = Inventory()
    inventory.add("hide", 4)
    equipment = Equipment()

    assert craft("hide_armor", inventory, equipment) is True
    assert craft("hide_armor", inventory, equipment) is True

    assert inventory.get("hide") == 0
    assert inventory.get("stone") == 0


def test_insufficient_resources() -> None:
    """Crafting fails when resources are insufficient."""
    inventory = Inventory()
    equipment = Equipment()

    inventory.spend({"wood": 5})

    result = craft("stone_spear", inventory, equipment)

    assert result is False
    assert equipment.has_stone_spear is False
    assert inventory.get("wood") == 0
    assert inventory.get("stone") == 2


def test_duplicate_spear_fails() -> None:
    """A stone spear cannot be crafted twice."""
    inventory = Inventory()
    equipment = Equipment()

    assert craft("stone_spear", inventory, equipment) is True

    wood_before = inventory.get("wood")
    stone_before = inventory.get("stone")

    assert craft("stone_spear", inventory, equipment) is False
    assert inventory.get("wood") == wood_before
    assert inventory.get("stone") == stone_before


def test_duplicate_axe_fails() -> None:
    """A stone axe cannot be crafted twice."""
    inventory = Inventory()
    equipment = Equipment()

    assert craft("stone_axe", inventory, equipment) is True

    wood_before = inventory.get("wood")
    stone_before = inventory.get("stone")

    assert craft("stone_axe", inventory, equipment) is False
    assert inventory.get("wood") == wood_before
    assert inventory.get("stone") == stone_before


def test_duplicate_torch_fails() -> None:
    """A torch cannot be crafted twice."""
    inventory = Inventory()
    equipment = Equipment()

    assert craft("torch", inventory, equipment) is True

    wood_before = inventory.get("wood")

    assert craft("torch", inventory, equipment) is False
    assert inventory.get("wood") == wood_before


def test_unknown_item_fails() -> None:
    """An unknown item cannot be crafted."""
    inventory = Inventory()
    equipment = Equipment()

    result = craft("unknown_item", inventory, equipment)

    assert result is False
    assert inventory.get("wood") == 5
    assert inventory.get("stone") == 2


def test_get_recipe_returns_copy() -> None:
    """get_recipe returns a copy rather than the original recipe."""
    recipe = get_recipe("stone_spear")

    assert recipe == {
        "wood": 2,
        "stone": 1,
    }

    assert recipe is not None

    recipe["wood"] = 999

    original = get_recipe("stone_spear")

    assert original is not None
    assert original["wood"] == 2


def test_unknown_recipe_returns_none() -> None:
    """Unknown recipes return None."""
    assert get_recipe("unknown_item") is None