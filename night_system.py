"""Night defense logic for Stone Age Survival.

This module contains pure game logic and must not depend on pygame.
"""

from __future__ import annotations

import random

from constants import (
    CAMP_POSITION,
    ENEMY_BOAR,
    ENEMY_WOLF,
    EVENT_WOLF_TRACKS,
    MAP_COLS,
    MAP_ROWS,
    TERRAIN_WATER,
)
from enemy import Enemy, create_enemy


HEX_DIRECTIONS = (
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
)


def hex_distance(
    a: tuple[int, int],
    b: tuple[int, int],
) -> int:
    """Return the axial hex-grid distance between two positions."""

    q1, r1 = a
    q2, r2 = b

    return (
        abs(q1 - q2)
        + abs(q1 + r1 - q2 - r2)
        + abs(r1 - r2)
    ) // 2


def get_next_enemy_position(
    enemy: Enemy,
    hex_map,
    campfire_lit: bool,
) -> tuple[int, int]:
    """Return one legal step toward the camp.

    The function does not move the enemy itself.

    Wolves refuse to enter the campfire protection zone while the
    campfire is lit. Boars ignore the fire.
    """

    if not enemy.alive:
        return enemy.position

    current_distance = hex_distance(
        enemy.position,
        CAMP_POSITION,
    )

    if current_distance == 0:
        return enemy.position

    q, r = enemy.position
    candidates: list[tuple[int, int]] = []

    for dq, dr in HEX_DIRECTIONS:
        candidate = (q + dq, r + dr)

        tile = hex_map.get_tile(
            candidate[0],
            candidate[1],
        )

        if tile is None:
            continue

        if tile.terrain == TERRAIN_WATER:
            continue

        candidate_distance = hex_distance(
            candidate,
            CAMP_POSITION,
        )

        # Only move closer to the camp.
        if candidate_distance >= current_distance:
            continue

        # Wolves avoid the camp and its six surrounding hexes
        # while the campfire is burning.
        if (
            enemy.fear_of_fire
            and campfire_lit
            and candidate_distance <= 1
        ):
            continue

        candidates.append(candidate)

    if not candidates:
        return enemy.position

    # Deterministic ordering makes tests reproducible.
    candidates.sort(
        key=lambda position: (
            hex_distance(position, CAMP_POSITION),
            position[0],
            position[1],
        )
    )

    return candidates[0]


def move_enemy_toward_camp(
    enemy: Enemy,
    hex_map,
    campfire_lit: bool,
) -> int:
    """Move an enemy toward camp and return the number of steps taken.

    Wolves may move up to two hexes each enemy round.
    Boars may move one hex.
    """

    if not enemy.alive:
        return 0

    steps_taken = 0

    for _ in range(enemy.move_range):
        next_position = get_next_enemy_position(
            enemy,
            hex_map,
            campfire_lit,
        )

        if next_position == enemy.position:
            break

        enemy.position = next_position
        steps_taken += 1

        if enemy.position == CAMP_POSITION:
            break

    return steps_taken


class NightSystem:
    """Manage enemy spawning and night-round state."""

    def __init__(
        self,
        rng: random.Random | None = None,
    ) -> None:
        self.rng = rng if rng is not None else random.Random()

        self.night_round = 0
        self.max_night_rounds = 4
        self.enemies: list[Enemy] = []
        self.active = False

    def get_enemy_counts(
        self,
        day: int,
        event_type: str,
    ) -> tuple[int, int]:
        """Return the wolf and boar counts for the specified night."""

        if day < 1:
            raise ValueError("Day must be at least 1.")

        if day == 1:
            wolf_count = 2
            boar_count = 0

        elif day == 2:
            wolf_count = 3
            boar_count = 0

        elif day == 3:
            wolf_count = 3
            boar_count = 1

        else:
            wolf_count = min(2 + day, 7)
            boar_count = min(day // 3, 3)

        if event_type == EVENT_WOLF_TRACKS:
            wolf_count += 2

        return wolf_count, boar_count

    def get_spawn_candidates(
        self,
        hex_map,
    ) -> list[tuple[int, int]]:
        """Return valid non-water tiles along the outside edge of the map."""

        candidates: list[tuple[int, int]] = []

        for q in range(MAP_COLS):
            for r in range(MAP_ROWS):
                is_edge = (
                    q == 0
                    or q == MAP_COLS - 1
                    or r == 0
                    or r == MAP_ROWS - 1
                )

                if not is_edge:
                    continue

                position = (q, r)

                if position == CAMP_POSITION:
                    continue

                tile = hex_map.get_tile(q, r)

                if tile is None:
                    continue

                if tile.terrain == TERRAIN_WATER:
                    continue

                candidates.append(position)

        return candidates

    def _choose_spawn_positions(
        self,
        candidates: list[tuple[int, int]],
        count: int,
    ) -> list[tuple[int, int]]:
        """Choose spawn positions, avoiding duplicates whenever possible."""

        if count < 0:
            raise ValueError("Spawn count cannot be negative.")

        if count == 0:
            return []

        if not candidates:
            raise ValueError("No valid enemy spawn positions are available.")

        shuffled = list(candidates)
        self.rng.shuffle(shuffled)

        if count <= len(shuffled):
            return shuffled[:count]

        positions = list(shuffled)

        while len(positions) < count:
            positions.append(
                self.rng.choice(candidates)
            )

        return positions

    def start_night(
        self,
        day: int,
        hex_map,
        event_type: str,
    ) -> None:
        """Start a night and spawn enemies on map-edge tiles."""

        wolf_count, boar_count = self.get_enemy_counts(
            day,
            event_type,
        )

        total_enemy_count = wolf_count + boar_count

        candidates = self.get_spawn_candidates(hex_map)

        spawn_positions = self._choose_spawn_positions(
            candidates,
            total_enemy_count,
        )

        self.enemies.clear()

        position_index = 0

        for _ in range(wolf_count):
            self.enemies.append(
                create_enemy(
                    ENEMY_WOLF,
                    spawn_positions[position_index],
                )
            )
            position_index += 1

        for _ in range(boar_count):
            self.enemies.append(
                create_enemy(
                    ENEMY_BOAR,
                    spawn_positions[position_index],
                )
            )
            position_index += 1

        self.night_round = 0
        self.active = True