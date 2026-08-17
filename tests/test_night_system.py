"""Tests for the night system."""

import random
from dataclasses import dataclass

import pytest

from constants import (
    ENEMY_BOAR,
    ENEMY_WOLF,
    EVENT_NONE,
    EVENT_WOLF_TRACKS,
    MAP_COLS,
    MAP_ROWS,
    TERRAIN_GRASS,
    TERRAIN_WATER,
)
from night_system import NightSystem, hex_distance


@dataclass
class FakeTile:
    """Minimal tile used only to test NightSystem integration contracts."""

    terrain: str = TERRAIN_GRASS


class FakeHexMap:
    """Minimal test double matching the expected HexMap get_tile API."""

    def __init__(self) -> None:
        self.tiles = {
            (q, r): FakeTile()
            for q in range(MAP_COLS)
            for r in range(MAP_ROWS)
        }

    def get_tile(
        self,
        q: int,
        r: int,
    ) -> FakeTile | None:
        return self.tiles.get((q, r))


def test_hex_distance_same_position():
    assert hex_distance((5, 4), (5, 4)) == 0


def test_hex_distance_adjacent_positions():
    assert hex_distance((5, 4), (6, 4)) == 1
    assert hex_distance((5, 4), (5, 3)) == 1
    assert hex_distance((5, 4), (4, 5)) == 1


def test_hex_distance_is_symmetric():
    a = (1, 2)
    b = (8, 6)

    assert hex_distance(a, b) == hex_distance(b, a)


def test_night_system_initial_state():
    system = NightSystem(random.Random(1))

    assert system.night_round == 0
    assert system.max_night_rounds == 4
    assert system.enemies == []
    assert system.active is False


def test_day_one_enemy_counts():
    system = NightSystem(random.Random(1))

    wolves, boars = system.get_enemy_counts(
        1,
        EVENT_NONE,
    )

    assert wolves == 2
    assert boars == 0


def test_day_two_enemy_counts():
    system = NightSystem(random.Random(1))

    wolves, boars = system.get_enemy_counts(
        2,
        EVENT_NONE,
    )

    assert wolves == 3
    assert boars == 0


def test_day_three_enemy_counts():
    system = NightSystem(random.Random(1))

    wolves, boars = system.get_enemy_counts(
        3,
        EVENT_NONE,
    )

    assert wolves == 3
    assert boars == 1


def test_day_four_enemy_counts():
    system = NightSystem(random.Random(1))

    wolves, boars = system.get_enemy_counts(
        4,
        EVENT_NONE,
    )

    assert wolves == 6
    assert boars == 1


def test_late_game_enemy_counts_are_capped():
    system = NightSystem(random.Random(1))

    wolves, boars = system.get_enemy_counts(
        20,
        EVENT_NONE,
    )

    assert wolves == 7
    assert boars == 3


def test_wolf_tracks_adds_two_wolves():
    system = NightSystem(random.Random(1))

    wolves, boars = system.get_enemy_counts(
        3,
        EVENT_WOLF_TRACKS,
    )

    assert wolves == 5
    assert boars == 1


def test_invalid_day_raises_value_error():
    system = NightSystem(random.Random(1))

    with pytest.raises(ValueError):
        system.get_enemy_counts(
            0,
            EVENT_NONE,
        )


def test_spawn_candidates_only_include_edges():
    hex_map = FakeHexMap()
    system = NightSystem(random.Random(1))

    candidates = system.get_spawn_candidates(hex_map)

    assert candidates

    for q, r in candidates:
        assert (
            q == 0
            or q == MAP_COLS - 1
            or r == 0
            or r == MAP_ROWS - 1
        )


def test_water_tiles_are_not_spawn_candidates():
    hex_map = FakeHexMap()

    hex_map.tiles[(0, 0)].terrain = TERRAIN_WATER
    hex_map.tiles[(10, 7)].terrain = TERRAIN_WATER

    system = NightSystem(random.Random(1))

    candidates = system.get_spawn_candidates(hex_map)

    assert (0, 0) not in candidates
    assert (10, 7) not in candidates


def test_start_night_day_one():
    hex_map = FakeHexMap()
    system = NightSystem(random.Random(10))

    system.start_night(
        1,
        hex_map,
        EVENT_NONE,
    )

    assert system.active is True
    assert system.night_round == 0
    assert len(system.enemies) == 2

    assert all(
        enemy.enemy_type == ENEMY_WOLF
        for enemy in system.enemies
    )


def test_start_night_day_three():
    hex_map = FakeHexMap()
    system = NightSystem(random.Random(10))

    system.start_night(
        3,
        hex_map,
        EVENT_NONE,
    )

    wolves = [
        enemy
        for enemy in system.enemies
        if enemy.enemy_type == ENEMY_WOLF
    ]

    boars = [
        enemy
        for enemy in system.enemies
        if enemy.enemy_type == ENEMY_BOAR
    ]

    assert len(wolves) == 3
    assert len(boars) == 1


def test_spawned_enemies_are_on_map_edge():
    hex_map = FakeHexMap()
    system = NightSystem(random.Random(15))

    system.start_night(
        4,
        hex_map,
        EVENT_NONE,
    )

    for enemy in system.enemies:
        q, r = enemy.position

        assert (
            q == 0
            or q == MAP_COLS - 1
            or r == 0
            or r == MAP_ROWS - 1
        )


def test_spawn_positions_do_not_repeat_when_enough_tiles_exist():
    hex_map = FakeHexMap()
    system = NightSystem(random.Random(99))

    system.start_night(
        4,
        hex_map,
        EVENT_NONE,
    )

    positions = [
        enemy.position
        for enemy in system.enemies
    ]

    assert len(positions) == len(set(positions))


def test_start_night_replaces_previous_enemies():
    hex_map = FakeHexMap()
    system = NightSystem(random.Random(1))

    system.start_night(
        1,
        hex_map,
        EVENT_NONE,
    )

    assert len(system.enemies) == 2

    system.start_night(
        3,
        hex_map,
        EVENT_NONE,
    )

    assert len(system.enemies) == 4


def test_seeded_spawn_is_reproducible():
    hex_map_a = FakeHexMap()
    hex_map_b = FakeHexMap()

    system_a = NightSystem(random.Random(42))
    system_b = NightSystem(random.Random(42))

    system_a.start_night(
        3,
        hex_map_a,
        EVENT_NONE,
    )

    system_b.start_night(
        3,
        hex_map_b,
        EVENT_NONE,
    )

    positions_a = [
        enemy.position
        for enemy in system_a.enemies
    ]

    positions_b = [
        enemy.position
        for enemy in system_b.enemies
    ]

    assert positions_a == positions_b


def test_no_spawn_candidates_raises_value_error():
    hex_map = FakeHexMap()

    for tile in hex_map.tiles.values():
        tile.terrain = TERRAIN_WATER

    system = NightSystem(random.Random(1))

    with pytest.raises(ValueError):
        system.start_night(
            1,
            hex_map,
            EVENT_NONE,
        )