"""Tests for the Survival system."""

import pytest

from inventory import Inventory
from survival import SurvivalStats


def test_default_values() -> None:
    """Survival starts with the required values."""
    stats = SurvivalStats()

    assert stats.health == 100
    assert stats.armor == 0
    assert stats.hunger == 20


def test_armor_absorbs_damage_first() -> None:
    """Armor absorbs damage before health."""
    stats = SurvivalStats()
    stats.armor = 10

    lost_health = stats.take_damage(15)

    assert lost_health == 5
    assert stats.armor == 0
    assert stats.health == 95


def test_damage_less_than_armor() -> None:
    """Damage smaller than armor does not reduce health."""
    stats = SurvivalStats()
    stats.armor = 10

    lost_health = stats.take_damage(6)

    assert lost_health == 0
    assert stats.armor == 4
    assert stats.health == 100


def test_health_cannot_go_below_zero() -> None:
    """Health is clamped at zero."""
    stats = SurvivalStats()

    lost_health = stats.take_damage(150)

    assert lost_health == 150
    assert stats.health == 0


def test_negative_damage_raises() -> None:
    """Negative damage raises ValueError."""
    stats = SurvivalStats()

    with pytest.raises(ValueError):
        stats.take_damage(-1)


def test_armor_max() -> None:
    """Armor cannot exceed MAX_ARMOR."""
    stats = SurvivalStats()

    stats.add_armor(100)

    assert stats.armor == 50


def test_negative_armor_raises() -> None:
    """Negative armor raises ValueError."""
    stats = SurvivalStats()

    with pytest.raises(ValueError):
        stats.add_armor(-1)


def test_hunger_max() -> None:
    """Hunger cannot exceed MAX_HUNGER."""
    stats = SurvivalStats()

    stats.increase_hunger(1000)

    assert stats.hunger == 100


def test_negative_hunger_raises() -> None:
    """Negative hunger raises ValueError."""
    stats = SurvivalStats()

    with pytest.raises(ValueError):
        stats.increase_hunger(-1)


def test_eat_one_food() -> None:
    """Eating one food reduces hunger by 25."""
    inventory = Inventory()
    stats = SurvivalStats()
    stats.hunger = 70

    result = stats.eat(inventory)

    assert result is True
    assert stats.hunger == 45
    assert inventory.get("food") == 2


def test_eat_two_food() -> None:
    """Eating two food reduces hunger by 50."""
    inventory = Inventory()
    stats = SurvivalStats()
    stats.hunger = 70

    result = stats.eat(inventory, 2)

    assert result is True
    assert stats.hunger == 20
    assert inventory.get("food") == 1


def test_eat_clamps_hunger_at_zero() -> None:
    """Eating cannot reduce hunger below zero."""
    inventory = Inventory()
    stats = SurvivalStats()
    stats.hunger = 10

    result = stats.eat(inventory)

    assert result is True
    assert stats.hunger == 0
    assert inventory.get("food") == 2


def test_eat_insufficient_food() -> None:
    """Eating fails without enough food."""
    inventory = Inventory()
    stats = SurvivalStats()
    stats.hunger = 50

    inventory.spend({"food": 3})

    result = stats.eat(inventory)

    assert result is False
    assert stats.hunger == 50
    assert inventory.get("food") == 0


def test_eat_zero() -> None:
    """Eating zero food returns False."""
    inventory = Inventory()
    stats = SurvivalStats()

    result = stats.eat(inventory, 0)

    assert result is False
    assert stats.hunger == 20
    assert inventory.get("food") == 3


def test_eat_negative_raises() -> None:
    """Eating a negative amount raises ValueError."""
    inventory = Inventory()
    stats = SurvivalStats()

    with pytest.raises(ValueError):
        stats.eat(inventory, -1)


def test_daily_hunger() -> None:
    """Daily hunger increases by 15."""
    stats = SurvivalStats()

    stats.apply_daily_hunger()

    assert stats.hunger == 35
    assert stats.health == 100


def test_daily_hunger_starvation_damage() -> None:
    """High hunger causes ten direct health damage."""
    stats = SurvivalStats()
    stats.hunger = 70
    stats.armor = 50

    stats.apply_daily_hunger()

    assert stats.hunger == 85
    assert stats.health == 90
    assert stats.armor == 50


def test_daily_hunger_clamps_at_100() -> None:
    """Daily hunger is clamped at 100."""
    stats = SurvivalStats()
    stats.hunger = 95

    stats.apply_daily_hunger()

    assert stats.hunger == 100
    assert stats.health == 90


def test_daily_hunger_damage_can_kill() -> None:
    """Starvation damage can reduce health to zero."""
    stats = SurvivalStats()
    stats.health = 5
    stats.hunger = 80

    stats.apply_daily_hunger()

    assert stats.health == 0
    assert stats.is_dead() is True


def test_is_dead_false_when_alive() -> None:
    """A player with positive health is alive."""
    stats = SurvivalStats()

    assert stats.is_dead() is False


def test_is_dead_true_at_zero() -> None:
    """A player with zero health is dead."""
    stats = SurvivalStats()
    stats.health = 0

    assert stats.is_dead() is True