"""Crafting and equipment system for Stone Age Survival."""

from dataclasses import dataclass

from constants import (
    RESOURCE_HIDE,
    RESOURCE_STONE,
    RESOURCE_WOOD,
)
from inventory import Inventory


RECIPES: dict[str, dict[str, int]] = {
    "stone_spear": {
        RESOURCE_WOOD: 2,
        RESOURCE_STONE: 1,
    },
    "stone_axe": {
        RESOURCE_WOOD: 1,
        RESOURCE_STONE: 2,
    },
    "hide_armor": {
        RESOURCE_HIDE: 2,
        RESOURCE_STONE: 1,
    },
    "torch": {
        RESOURCE_WOOD: 1,
    },
}


@dataclass
class Equipment:
    """Store the player's permanent crafted equipment."""

    has_stone_spear: bool = False
    has_stone_axe: bool = False
    has_torch: bool = False


def get_recipe(item_name: str) -> dict[str, int] | None:
    """Return a copy of an item's recipe, or None if unknown."""
    recipe = RECIPES.get(item_name)

    if recipe is None:
        return None

    return recipe.copy()


def craft(
    item_name: str,
    inventory: Inventory,
    equipment: Equipment,
) -> bool:
    """Craft an item if its recipe and required resources are available."""
    recipe = get_recipe(item_name)

    if recipe is None:
        return False

    if item_name == "stone_spear" and equipment.has_stone_spear:
        return False

    if item_name == "stone_axe" and equipment.has_stone_axe:
        return False

    if item_name == "torch" and equipment.has_torch:
        return False

    if not inventory.spend(recipe):
        return False

    if item_name == "stone_spear":
        equipment.has_stone_spear = True

    elif item_name == "stone_axe":
        equipment.has_stone_axe = True

    elif item_name == "torch":
        equipment.has_torch = True

    # hide_armor intentionally does not modify SurvivalStats.
    # The integration layer applies HIDE_ARMOR_BONUS.

    return True