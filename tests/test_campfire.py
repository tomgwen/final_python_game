import pytest

from campfire import Campfire
from constants import CAMPFIRE_MAX_FUEL
from inventory import Inventory


def test_campfire_starts_lit_with_three_fuel():
    campfire = Campfire((5, 4))

    assert campfire.position == (5, 4)
    assert campfire.fuel == 3
    assert campfire.lit is True


def test_add_one_wood_adds_two_fuel():
    inventory = Inventory()
    campfire = Campfire((5, 4))

    wood_before = inventory.get("wood")

    assert campfire.add_fuel(inventory) is True

    assert campfire.fuel == 5
    assert inventory.get("wood") == wood_before - 1


def test_add_multiple_wood():
    inventory = Inventory()
    campfire = Campfire((5, 4))

    assert campfire.add_fuel(inventory, 2) is True
    assert campfire.fuel == 7


def test_fuel_is_capped_at_maximum():
    inventory = Inventory()
    campfire = Campfire((5, 4))

    campfire.fuel = 11

    assert campfire.add_fuel(inventory, 1) is True
    assert campfire.fuel == CAMPFIRE_MAX_FUEL


def test_extra_fuel_can_be_wasted_at_maximum():
    inventory = Inventory()
    campfire = Campfire((5, 4))

    campfire.fuel = CAMPFIRE_MAX_FUEL
    wood_before = inventory.get("wood")

    assert campfire.add_fuel(inventory, 1) is True

    assert campfire.fuel == CAMPFIRE_MAX_FUEL
    assert inventory.get("wood") == wood_before - 1


def test_add_fuel_fails_without_enough_wood():
    inventory = Inventory()
    campfire = Campfire((5, 4))

    inventory.spend({"wood": inventory.get("wood")})

    fuel_before = campfire.fuel

    assert campfire.add_fuel(inventory) is False
    assert campfire.fuel == fuel_before


def test_add_fuel_to_unlit_fire_fails():
    inventory = Inventory()
    campfire = Campfire((5, 4))

    campfire.consume(3)

    wood_before = inventory.get("wood")

    assert campfire.add_fuel(inventory) is False
    assert campfire.lit is False
    assert inventory.get("wood") == wood_before


def test_negative_add_fuel_raises_value_error():
    inventory = Inventory()
    campfire = Campfire((5, 4))

    with pytest.raises(ValueError):
        campfire.add_fuel(inventory, -1)


def test_zero_add_fuel_does_nothing():
    inventory = Inventory()
    campfire = Campfire((5, 4))

    fuel_before = campfire.fuel
    wood_before = inventory.get("wood")

    assert campfire.add_fuel(inventory, 0) is False
    assert campfire.fuel == fuel_before
    assert inventory.get("wood") == wood_before


def test_consume_reduces_fuel():
    campfire = Campfire((5, 4))

    campfire.consume()

    assert campfire.fuel == 2
    assert campfire.lit is True


def test_consume_can_extinguish_fire():
    campfire = Campfire((5, 4))

    campfire.consume(3)

    assert campfire.fuel == 0
    assert campfire.lit is False


def test_consume_clamps_at_zero():
    campfire = Campfire((5, 4))

    campfire.consume(100)

    assert campfire.fuel == 0
    assert campfire.lit is False


def test_negative_consume_raises_value_error():
    campfire = Campfire((5, 4))

    with pytest.raises(ValueError):
        campfire.consume(-1)


def test_relight_costs_one_wood_and_sets_two_fuel():
    inventory = Inventory()
    campfire = Campfire((5, 4))

    campfire.consume(3)

    wood_before = inventory.get("wood")

    assert campfire.relight(inventory) is True

    assert campfire.lit is True
    assert campfire.fuel == 2
    assert inventory.get("wood") == wood_before - 1


def test_relight_lit_fire_fails_without_spending_wood():
    inventory = Inventory()
    campfire = Campfire((5, 4))

    wood_before = inventory.get("wood")

    assert campfire.relight(inventory) is False
    assert inventory.get("wood") == wood_before


def test_relight_fails_without_wood():
    inventory = Inventory()
    campfire = Campfire((5, 4))

    campfire.consume(3)
    inventory.spend({"wood": inventory.get("wood")})

    assert campfire.relight(inventory) is False
    assert campfire.lit is False
    assert campfire.fuel == 0


def test_light_radius_zero_when_unlit():
    campfire = Campfire((5, 4))

    campfire.consume(3)

    assert campfire.get_light_radius() == 0


def test_light_radius_one_for_fuel_one_to_three():
    campfire = Campfire((5, 4))

    campfire.fuel = 1
    assert campfire.get_light_radius() == 1

    campfire.fuel = 3
    assert campfire.get_light_radius() == 1


def test_light_radius_two_for_fuel_four_to_seven():
    campfire = Campfire((5, 4))

    campfire.fuel = 4
    assert campfire.get_light_radius() == 2

    campfire.fuel = 7
    assert campfire.get_light_radius() == 2


def test_light_radius_three_for_fuel_eight_to_twelve():
    campfire = Campfire((5, 4))

    campfire.fuel = 8
    assert campfire.get_light_radius() == 3

    campfire.fuel = 12
    assert campfire.get_light_radius() == 3