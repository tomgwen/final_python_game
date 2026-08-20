"""Enemy logic for Stone Age Survival.

This module contains only pure game logic and must not depend on pygame.
"""

from dataclasses import dataclass

from constants import (
    ENEMY_BEAR,
    ENEMY_BOAR,
    ENEMY_HYENA,
    ENEMY_SABERTOOTH,
    ENEMY_WOLF,
    PLAYER_BASE_DAMAGE,
    PLAYER_SPEAR_DAMAGE,
    RESOURCE_FOOD,
    RESOURCE_HIDE,
)

ENEMY_STATS = {
    ENEMY_WOLF: {
        "name": "狼",
        "health": 30,
        "damage": 6,
        "move_range": 2,
        "fear_of_fire": True,
        "start_day": 1,
        "spawn_weight": 5,
        "wall_damage": 10,
        "loot": {
            RESOURCE_HIDE: 1,
        },
    },
    ENEMY_BOAR: {
        "name": "野豬",
        "health": 55,
        "damage": 10,
        "move_range": 1,
        "fear_of_fire": False,
        "start_day": 2,
        "spawn_weight": 4,
        "wall_damage": 25,
        "loot": {
            RESOURCE_HIDE: 1,
            RESOURCE_FOOD: 1,
        },
    },
    ENEMY_HYENA: {
        "name": "鬣狗",
        "health": 40,
        "damage": 8,
        "move_range": 2,
        "fear_of_fire": True,
        "start_day": 4,
        "wall_damage": 12,
        "spawn_weight": 3,
        "loot": {
            RESOURCE_HIDE: 1,
            RESOURCE_FOOD: 1,
        },
    },
    ENEMY_BEAR: {
        "name": "熊",
        "health": 90,
        "damage": 16,
        "move_range": 1,
        "fear_of_fire": False,
        "start_day": 6,
        "wall_damage": 30,
        "spawn_weight": 2,
        "loot": {
            RESOURCE_HIDE: 2,
            RESOURCE_FOOD: 2,
        },
    },
    ENEMY_SABERTOOTH: {
        "name": "劍齒虎",
        "health": 70,
        "damage": 18,
        "move_range": 2,
        "fear_of_fire": False,
        "start_day": 9,
        "wall_damage": 22,
        "spawn_weight": 1,
        "loot": {
            RESOURCE_HIDE: 2,
            RESOURCE_FOOD: 2,
        },
    },
}

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

    stats = ENEMY_STATS.get(enemy_type)

    if stats is None:
        raise ValueError(f"Unknown enemy type: {enemy_type}")

    return Enemy(
        enemy_type=enemy_type,
        position=position,
        health=stats["health"],
        damage=stats["damage"],
        move_range=stats["move_range"],
        fear_of_fire=stats["fear_of_fire"],
    )

def get_enemy_name(enemy_type: str) -> str:
    stats = ENEMY_STATS.get(enemy_type)

    if stats is None:
        return enemy_type

    return stats["name"]

def get_enemy_wall_damage(enemy_type: str) -> int:
    stats = ENEMY_STATS.get(enemy_type)

    if stats is None:
        raise ValueError(f"Unknown enemy type: {enemy_type}")

    return stats["wall_damage"]

def get_enemy_max_health(enemy_type: str) -> int:
    stats = ENEMY_STATS.get(enemy_type)

    if stats is None:
        raise ValueError(f"Unknown enemy type: {enemy_type}")

    return stats["health"]

def get_enemy_start_day(enemy_type: str) -> int:
    stats = ENEMY_STATS.get(enemy_type)

    if stats is None:
        raise ValueError(f"Unknown enemy type: {enemy_type}")

    return stats["start_day"]


def available_enemy_types(day: int) -> list[str]:
    """Return enemy types unlocked by the given day."""
    return [
        enemy_type
        for enemy_type, stats in ENEMY_STATS.items()
        if day >= stats["start_day"]
    ]

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

    stats = ENEMY_STATS.get(enemy.enemy_type)

    if stats is None:
        return {}

    return dict(stats["loot"])

    return {}
