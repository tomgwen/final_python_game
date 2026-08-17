"""Enemy logic for Stone Age Survival.

This module contains only pure game logic and must not depend on pygame.
"""

from dataclasses import dataclass

from constants import (
    ENEMY_BOAR,
    ENEMY_WOLF,
    PLAYER_BASE_DAMAGE,
    PLAYER_SPEAR_DAMAGE,
    RESOURCE_FOOD,
    RESOURCE_HIDE,
)


@dataclass
class Enemy:
    """Represents a hostile creature during the night phase."""

    enemy_type: str
    position: tuple[int, int]
    health: int
    damage: int
    move_range: int
    fear_of_fire: bool
    alive: bool = True
    loot_claimed: bool = False


def create_enemy(
    enemy_type: str,
    position: tuple[int, int],
) -> Enemy:
    """Create an enemy with the correct statistics for its type."""

    if enemy_type == ENEMY_WOLF:
        return Enemy(
            enemy_type=ENEMY_WOLF,
            position=position,
            health=30,
            damage=10,
            move_range=2,
            fear_of_fire=True,
        )

    if enemy_type == ENEMY_BOAR:
        return Enemy(
            enemy_type=ENEMY_BOAR,
            position=position,
            health=55,
            damage=15,
            move_range=1,
            fear_of_fire=False,
        )

    raise ValueError(f"Unknown enemy type: {enemy_type}")


def damage_enemy(
    enemy: Enemy,
    damage: int,
) -> bool:
    """Apply damage and return True if the enemy is dead."""

    if damage < 0:
        raise ValueError("Damage cannot be negative.")

    if not enemy.alive:
        return True

    enemy.health = max(0, enemy.health - damage)

    if enemy.health == 0:
        enemy.alive = False
        return True

    return False


def calculate_player_damage(
    has_stone_spear: bool,
) -> int:
    """Return the player's attack damage based on equipment."""

    if has_stone_spear:
        return PLAYER_SPEAR_DAMAGE

    return PLAYER_BASE_DAMAGE


def claim_loot(
    enemy: Enemy,
) -> dict[str, int]:
    """Return loot from a dead enemy.

    Loot may only be claimed once.
    """

    if enemy.alive:
        return {}

    if enemy.loot_claimed:
        return {}

    enemy.loot_claimed = True

    if enemy.enemy_type == ENEMY_WOLF:
        return {
            RESOURCE_HIDE: 1,
        }

    if enemy.enemy_type == ENEMY_BOAR:
        return {
            RESOURCE_HIDE: 1,
            RESOURCE_FOOD: 1,
        }

    return {}
