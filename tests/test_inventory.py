"""Tests for the Inventory system."""

import pytest

from inventory import Inventory
from constants import (
    RESOURCE_FOOD,
    RESOURCE_HIDE,
    RESOURCE_STONE,
    RESOURCE_WOOD,
)


def test_default_values() -> None:
    """Inventory starts with the required default resources."""
    inventory = Inventory()

    assert inventory.get(RESOURCE_FOOD) == 3
    assert inventory.get(RESOURCE_WOOD) == 5
    assert inventory.get(RESOURCE_STONE) == 2
    assert inventory.get(RESOURCE_HIDE) == 0


def test_get_resource() -> None:
    """get returns the current resource amount."""
    inventory = Inventory()

    assert inventory.get(RESOURCE_WOOD) == 5


def test_add_resource() -> None:
    """add increases the resource amount."""
    inventory = Inventory()

    inventory.add(RESOURCE_WOOD, 3)

    assert inventory.get(RESOURCE_WOOD) == 8


def test_add_zero() -> None:
    """Adding zero does not change the inventory."""
    inventory = Inventory()

    inventory.add(RESOURCE_WOOD, 0)

    assert inventory.get(RESOURCE_WOOD) == 5


def test_add_negative_raises() -> None:
    """Adding a negative amount raises ValueError."""
    inventory = Inventory()

    with pytest.raises(ValueError):
        inventory.add(RESOURCE_WOOD, -1)


def test_unknown_resource_raises() -> None:
    """Unknown resources raise ValueError."""
    inventory = Inventory()

    with pytest.raises(ValueError):
        inventory.get("gold")


def test_has_cost() -> None:
    """has returns True when the inventory can afford the cost."""
    inventory = Inventory()

    assert inventory.has({
        RESOURCE_WOOD: 3,
        RESOURCE_STONE: 1,
    })


def test_has_insufficient_cost() -> None:
    """has returns False when resources are insufficient."""
    inventory = Inventory()

    assert not inventory.has({
        RESOURCE_WOOD: 99,
    })


def test_spend_success() -> None:
    """spend removes the requested resources."""
    inventory = Inventory()

    result = inventory.spend({
        RESOURCE_WOOD: 2,
        RESOURCE_STONE: 1,
    })

    assert result is True
    assert inventory.get(RESOURCE_WOOD) == 3
    assert inventory.get(RESOURCE_STONE) == 1


def test_spend_insufficient_is_atomic() -> None:
    """Insufficient spending changes nothing."""
    inventory = Inventory()

    result = inventory.spend({
        RESOURCE_WOOD: 99,
        RESOURCE_STONE: 1,
    })

    assert result is False
    assert inventory.get(RESOURCE_WOOD) == 5
    assert inventory.get(RESOURCE_STONE) == 2


def test_negative_cost_raises() -> None:
    """Negative costs raise ValueError."""
    inventory = Inventory()

    with pytest.raises(ValueError):
        inventory.has({
            RESOURCE_WOOD: -1,
        })


def test_spend_negative_cost_raises() -> None:
    """Negative spending costs raise ValueError."""
    inventory = Inventory()

    with pytest.raises(ValueError):
        inventory.spend({
            RESOURCE_WOOD: -1,
        })
        