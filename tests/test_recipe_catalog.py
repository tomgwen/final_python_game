from recipe_catalog import (
    RECIPE_CATALOG,
    get_recipe,
    get_recipes_by_category,
)


def test_catalog_contains_expected_six_recipes():
    assert len(RECIPE_CATALOG) == 8

    ids = {
        recipe["id"]
        for recipe in RECIPE_CATALOG
    }

    assert ids == {
        "spear",
        "axe",
        "bow",
        "arrows",
        "armor",
        "pickaxe",
        "wall",
        "trap",
    }

def test_spear_recipe_values():
    recipe = get_recipe("spear")

    assert recipe is not None
    assert recipe["name"] == "石矛"
    assert recipe["category"] == "裝備"
    assert recipe["cost"] == {
        "wood": 2,
        "stone": 1,
    }


def test_axe_recipe_values():
    recipe = get_recipe("axe")

    assert recipe is not None
    assert recipe["cost"] == {
        "wood": 1,
        "stone": 2,
    }

    assert "2" in recipe["effect"]


def test_armor_recipe_values():
    recipe = get_recipe("armor")

    assert recipe is not None
    assert recipe["cost"] == {
        "hide": 2,
        "stone": 1,
    }

    assert "25" in recipe["effect"]
    assert "50" in recipe["effect"]


def test_wall_recipe_values():
    recipe = get_recipe("wall")

    assert recipe is not None
    assert recipe["category"] == "建造"
    assert recipe["cost"] == {
        "wood": 3,
    }

    assert "60" in recipe["effect"]


def test_trap_recipe_values():
    recipe = get_recipe("trap")

    assert recipe is not None
    assert recipe["cost"] == {
        "wood": 2,
        "stone": 1,
    }

    assert "25" in recipe["effect"]


def test_get_unknown_recipe_returns_none():
    assert get_recipe("unknown") is None


def test_get_equipment_recipes():
    recipes = get_recipes_by_category("裝備")

    assert [
        recipe["id"]
        for recipe in recipes
    ] == [
        "spear",
        "axe",
        "bow",
        "arrows",
        "armor",
        "pickaxe",
    ]


def test_get_building_recipes():
    recipes = get_recipes_by_category("建造")

    assert [
        recipe["id"]
        for recipe in recipes
    ] == [
        "wall",
        "trap",
    ]
