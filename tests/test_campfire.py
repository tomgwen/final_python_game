from campfire import CAMPFIRE_COST, Campfire
from inventory import Inventory


def test_campfire_starts_unlit():
    campfire = Campfire((2, 3))

    assert campfire.position == (2, 3)
    assert campfire.is_lit is False
    assert campfire.can_heal() is False
    assert campfire.heal_amount() == 0


def test_light_campfire_success():
    inventory = Inventory()
    campfire = Campfire((2, 3))

    assert campfire.light(inventory) is True
    assert campfire.is_lit is True
    assert campfire.can_heal() is True
    assert campfire.heal_amount() == 10
    assert inventory.get("wood") == 1
    assert inventory.get("stone") == 0


def test_light_campfire_requires_resources():
    inventory = Inventory()
    campfire = Campfire((2, 3))

    inventory.spend(CAMPFIRE_COST)

    assert campfire.light(inventory) is False
    assert campfire.is_lit is False


def test_lit_campfire_cannot_be_lit_again():
    inventory = Inventory()
    campfire = Campfire((2, 3))

    assert campfire.light(inventory) is True

    wood_before = inventory.get("wood")
    stone_before = inventory.get("stone")

    assert campfire.light(inventory) is False
    assert inventory.get("wood") == wood_before
    assert inventory.get("stone") == stone_before


def test_extinguish_campfire():
    inventory = Inventory()
    campfire = Campfire((2, 3))

    campfire.light(inventory)
    campfire.extinguish()

    assert campfire.is_lit is False
    assert campfire.can_heal() is False
    assert campfire.heal_amount() == 0


def test_extinguished_campfire_can_be_lit_again():
    inventory = Inventory()
    campfire = Campfire((2, 3))

    assert campfire.light(inventory) is True
    campfire.extinguish()

    inventory.add("wood", 4)
    inventory.add("stone", 2)

    assert campfire.light(inventory) is True
    assert campfire.is_lit is True


def test_heal_amount_is_zero_when_unlit():
    campfire = Campfire((2, 3))

    assert campfire.heal_amount() == 0


def test_heal_amount_is_ten_when_lit():
    inventory = Inventory()
    campfire = Campfire((2, 3))

    campfire.light(inventory)

    assert campfire.heal_amount() == 10
