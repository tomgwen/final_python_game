"""Tests for the enemy subsystem."""

import pytest

from constants import (
    ENEMY_BOAR,
    ENEMY_WOLF,
    PLAYER_BASE_DAMAGE,
    PLAYER_SPEAR_DAMAGE,
    RESOURCE_FOOD,
    RESOURCE_HIDE,
)
from enemy import (
    calculate_player_damage,
    claim_loot,
    create_enemy,
    damage_enemy,
)


def test_create_wolf():
    wolf = create_enemy(ENEMY_WOLF, (0, 0))

    assert wolf.enemy_type == ENEMY_WOLF
    assert wolf.position == (0, 0)
    assert wolf.health == 30
    assert wolf.damage == 6
    assert wolf.move_range == 2
    assert wolf.fear_of_fire is True
    assert wolf.alive is True
    assert wolf.loot_claimed is False


def test_create_boar():
    boar = create_enemy(ENEMY_BOAR, (10, 7))

    assert boar.enemy_type == ENEMY_BOAR
    assert boar.position == (10, 7)
    assert boar.health == 55
    assert boar.damage == 10
    assert boar.move_range == 1
    assert boar.fear_of_fire is False
    assert boar.alive is True
    assert boar.loot_claimed is False


def test_invalid_enemy_type():
    with pytest.raises(ValueError):
        create_enemy("mammoth", (0, 0))


def test_damage_enemy_without_killing():
    wolf = create_enemy(ENEMY_WOLF, (0, 0))

    died = damage_enemy(wolf, 10)

    assert died is False
    assert wolf.health == 20
    assert wolf.alive is True


def test_damage_enemy_kills_enemy():
    wolf = create_enemy(ENEMY_WOLF, (0, 0))

    died = damage_enemy(wolf, 30)

    assert died is True
    assert wolf.health == 0
    assert wolf.alive is False


def test_damage_cannot_make_health_negative():
    wolf = create_enemy(ENEMY_WOLF, (0, 0))

    died = damage_enemy(wolf, 100)

    assert died is True
    assert wolf.health == 0
    assert wolf.alive is False


def test_negative_damage_raises_value_error():
    wolf = create_enemy(ENEMY_WOLF, (0, 0))

    with pytest.raises(ValueError):
        damage_enemy(wolf, -1)


def test_damage_already_dead_enemy():
    wolf = create_enemy(ENEMY_WOLF, (0, 0))

    damage_enemy(wolf, 100)
    died = damage_enemy(wolf, 10)

    assert died is True
    assert wolf.health == 0


def test_player_base_damage():
    assert calculate_player_damage(False) == PLAYER_BASE_DAMAGE
    assert calculate_player_damage(False) == 10


def test_player_spear_damage():
    assert calculate_player_damage(True) == PLAYER_SPEAR_DAMAGE
    assert calculate_player_damage(True) == 20


def test_living_enemy_has_no_loot():
    wolf = create_enemy(ENEMY_WOLF, (0, 0))

    assert claim_loot(wolf) == {}
    assert wolf.loot_claimed is False


def test_wolf_loot():
    wolf = create_enemy(ENEMY_WOLF, (0, 0))
    damage_enemy(wolf, 30)

    loot = claim_loot(wolf)

    assert loot == {
        RESOURCE_HIDE: 1,
    }
    assert wolf.loot_claimed is True


def test_boar_loot():
    boar = create_enemy(ENEMY_BOAR, (0, 0))
    damage_enemy(boar, 55)

    loot = claim_loot(boar)

    assert loot == {
        RESOURCE_HIDE: 1,
        RESOURCE_FOOD: 1,
    }
    assert boar.loot_claimed is True


def test_loot_can_only_be_claimed_once():
    wolf = create_enemy(ENEMY_WOLF, (0, 0))
    damage_enemy(wolf, 30)

    first_loot = claim_loot(wolf)
    second_loot = claim_loot(wolf)

    assert first_loot == {
        RESOURCE_HIDE: 1,
    }
    assert second_loot == {}
