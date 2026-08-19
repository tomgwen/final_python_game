"""Display catalog for crafting and building recipes.

This module contains UI-facing recipe information only.
It must not import pygame or modify gameplay state.
"""

from __future__ import annotations


RECIPE_CATALOG = [
    {
        "id": "spear",
        "name": "石矛",
        "category": "裝備",
        "cost": {
            "wood": 2,
            "stone": 1,
        },
        "cost_text": "木材 x2、石頭 x1",
        "effect": "玩家攻擊力由 10 提升至 20",
    },
    {
        "id": "axe",
        "name": "石斧",
        "category": "裝備",
        "cost": {
            "wood": 1,
            "stone": 2,
        },
        "cost_text": "木材 x1、石頭 x2",
        "effect": "採集木材時，每次最多獲得 2 木材",
    },
    {
        "id": "armor",
        "name": "獸皮護甲",
        "category": "裝備",
        "cost": {
            "hide": 2,
            "stone": 1,
        },
        "cost_text": "獸皮 x2、石頭 x1",
        "effect": "增加 25 點護甲，護甲最高 50",
    },
    {
        "id": "pickaxe",
        "name": "石鎬",
        "category": "裝備",
        "cost": {"wood": 2, "stone": 2},
        "cost_text": "木材 x2、石頭 x2",
        "effect": "採集石頭時，每次最多獲得 2 石頭",
    },
    {
        "id": "wall",
        "name": "木牆",
        "category": "建造",
        "cost": {
            "wood": 3,
        },
        "cost_text": "木材 x3",
        "effect": "HP 60，可阻擋敵人前進",
    },
    {
        "id": "trap",
        "name": "陷阱",
        "category": "建造",
        "cost": {
            "wood": 2,
            "stone": 1,
        },
        "cost_text": "木材 x2、石頭 x1",
        "effect": "敵人第一次踩到時造成 25 點傷害",
    },
]


def get_recipe(recipe_id: str) -> dict | None:
    """Return one recipe by its stable id."""
    for recipe in RECIPE_CATALOG:
        if recipe["id"] == recipe_id:
            return recipe

    return None


def get_recipes_by_category(category: str) -> list[dict]:
    """Return all recipes belonging to a category."""
    return [
        recipe
        for recipe in RECIPE_CATALOG
        if recipe["category"] == category
    ]
