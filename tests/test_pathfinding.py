from pathfinding import (
    find_hex_path,
    get_hex_neighbors,
    is_valid_position,
)


def test_valid_position():
    assert is_valid_position((0, 0)) is True
    assert is_valid_position((10, 7)) is True

    assert is_valid_position((-1, 0)) is False
    assert is_valid_position((0, -1)) is False
    assert is_valid_position((11, 0)) is False
    assert is_valid_position((0, 8)) is False


def test_hex_neighbors_at_center():
    neighbors = get_hex_neighbors((5, 4))

    assert len(neighbors) == 6
    assert (6, 4) in neighbors
    assert (5, 3) in neighbors
    assert (4, 5) in neighbors


def test_path_to_same_tile_costs_zero():
    path = find_hex_path(
        (5, 4),
        (5, 4),
        is_walkable=lambda position: True,
    )

    assert path == [(5, 4)]
    assert len(path) - 1 == 0


def test_shortest_path_to_adjacent_tile():
    path = find_hex_path(
        (5, 4),
        (6, 4),
        is_walkable=lambda position: True,
    )

    assert path == [
        (5, 4),
        (6, 4),
    ]

    assert len(path) - 1 == 1


def test_path_avoids_water():
    water = {
        (6, 4),
    }

    path = find_hex_path(
        (5, 4),
        (7, 4),
        is_walkable=lambda position: (
            position not in water
        ),
    )

    assert path is not None
    assert (6, 4) not in path

    # A detour is required because the direct middle tile is water.
    assert len(path) - 1 > 2


def test_path_avoids_blocked_enemy_tile():
    blocked = {
        (6, 4),
    }

    path = find_hex_path(
        (5, 4),
        (7, 4),
        is_walkable=lambda position: True,
        blocked=blocked,
    )

    assert path is not None
    assert (6, 4) not in path


def test_blocked_goal_has_no_path():
    path = find_hex_path(
        (5, 4),
        (6, 4),
        is_walkable=lambda position: True,
        blocked={(6, 4)},
    )

    assert path is None


def test_unwalkable_goal_has_no_path():
    path = find_hex_path(
        (5, 4),
        (6, 4),
        is_walkable=lambda position: (
            position != (6, 4)
        ),
    )

    assert path is None