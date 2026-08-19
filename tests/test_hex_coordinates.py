import math

from hex_coordinates import (
    axial_to_world_pixel,
    world_to_axial_nearest,
)


HEX_SIZE = 30
COLS = 22
ROWS = 16
ORIGIN = (62, 140)


def test_origin_tile_maps_to_origin_pixel():
    x, y = axial_to_world_pixel(
        (0, 0),
        HEX_SIZE,
        ORIGIN,
    )

    assert x == ORIGIN[0]
    assert y == ORIGIN[1]


def test_axial_to_world_pixel_matches_existing_formula():
    q = 5
    r = 4

    expected_x = (
        ORIGIN[0]
        + HEX_SIZE
        * math.sqrt(3)
        * (q + r / 2)
    )

    expected_y = (
        ORIGIN[1]
        + HEX_SIZE
        * 1.5
        * r
    )

    actual_x, actual_y = axial_to_world_pixel(
        (q, r),
        HEX_SIZE,
        ORIGIN,
    )

    assert math.isclose(actual_x, expected_x)
    assert math.isclose(actual_y, expected_y)


def test_different_tiles_have_different_world_positions():
    a = axial_to_world_pixel(
        (5, 4),
        HEX_SIZE,
        ORIGIN,
    )

    b = axial_to_world_pixel(
        (6, 4),
        HEX_SIZE,
        ORIGIN,
    )

    assert a != b


def test_nearest_tile_finds_exact_hex_center():
    tile = (8, 7)

    center = axial_to_world_pixel(
        tile,
        HEX_SIZE,
        ORIGIN,
    )

    result = world_to_axial_nearest(
        center,
        HEX_SIZE,
        COLS,
        ROWS,
        ORIGIN,
    )

    assert result == tile


def test_nearest_tile_handles_far_corner_of_large_world():
    tile = (
        COLS - 1,
        ROWS - 1,
    )

    center = axial_to_world_pixel(
        tile,
        HEX_SIZE,
        ORIGIN,
    )

    result = world_to_axial_nearest(
        center,
        HEX_SIZE,
        COLS,
        ROWS,
        ORIGIN,
    )

    assert result == tile


def test_world_position_far_outside_map_returns_none():
    result = world_to_axial_nearest(
        (-10000, -10000),
        HEX_SIZE,
        COLS,
        ROWS,
        ORIGIN,
    )

    assert result is None


def test_small_offset_from_center_still_selects_same_tile():
    tile = (10, 8)

    center_x, center_y = axial_to_world_pixel(
        tile,
        HEX_SIZE,
        ORIGIN,
    )

    result = world_to_axial_nearest(
        (
            center_x + 5,
            center_y - 5,
        ),
        HEX_SIZE,
        COLS,
        ROWS,
        ORIGIN,
    )

    assert result == tile