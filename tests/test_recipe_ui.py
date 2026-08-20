import pygame

from main import (
    HUD_PANEL,
    recipe_button_rect,
    recipe_close_rect,
    recipe_modal_rect,
)
from recipe_catalog import RECIPE_CATALOG


def test_recipe_button_is_inside_hud():
    button = recipe_button_rect()

    assert HUD_PANEL.contains(button)


def test_recipe_modal_close_button_is_inside_modal():
    modal = recipe_modal_rect()
    close = recipe_close_rect()

    assert modal.contains(close)


def test_recipe_modal_has_all_catalog_items():
    assert len(RECIPE_CATALOG) == 8

    names = [
        recipe["name"]
        for recipe in RECIPE_CATALOG
    ]

    assert names == [
        "石矛",
        "石斧",
        "弓",
        "箭矢 x5",
        "獸皮護甲",
        "石鎬",
        "木牆",
        "陷阱",
    ]


def test_recipe_button_does_not_overlap_close_button():
    assert not recipe_button_rect().colliderect(
        recipe_close_rect()
    )
