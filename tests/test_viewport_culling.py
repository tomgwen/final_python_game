from __future__ import annotations

import pygame

from camera import Camera
from hex_coordinates import axial_to_world_pixel
from viewport_culling import tile_is_in_viewport, visible_world_tiles


HEX_SIZE = 30
ORIGIN = (62, 140)


def test_tile_near_viewport_center_is_visible_without_camera_offset() -> None:
    camera = Camera()
    viewport_rect = pygame.Rect(0, 0, 400, 300)

    assert tile_is_in_viewport(
        (0, 0),
        camera,
        viewport_rect,
        hex_size=HEX_SIZE,
        origin=ORIGIN,
    )


def test_tile_far_from_viewport_is_not_visible() -> None:
    camera = Camera()
    viewport_rect = pygame.Rect(0, 0, 400, 300)

    assert not tile_is_in_viewport(
        (10, 10),
        camera,
        viewport_rect,
        hex_size=HEX_SIZE,
        origin=ORIGIN,
    )


def test_camera_movement_changes_visibility_for_same_tile() -> None:
    camera = Camera()
    viewport_rect = pygame.Rect(0, 0, 400, 300)
    tile = (10, 10)
    world_pos = axial_to_world_pixel(tile, HEX_SIZE, ORIGIN)

    assert not tile_is_in_viewport(
        tile,
        camera,
        viewport_rect,
        hex_size=HEX_SIZE,
        origin=ORIGIN,
    )

    camera.center_on(world_pos, viewport_rect)

    assert tile_is_in_viewport(
        tile,
        camera,
        viewport_rect,
        hex_size=HEX_SIZE,
        origin=ORIGIN,
    )


def test_margin_keeps_tile_slightly_outside_viewport_visible() -> None:
    camera = Camera()
    viewport_rect = pygame.Rect(0, 0, 100, 101)

    assert tile_is_in_viewport(
        (0, 0),
        camera,
        viewport_rect,
        hex_size=HEX_SIZE,
        origin=ORIGIN,
        margin=40.0,
    )


def test_zero_margin_uses_strict_tile_center_check() -> None:
    camera = Camera()
    viewport_rect = pygame.Rect(0, 0, 100, 101)

    assert not tile_is_in_viewport(
        (0, 0),
        camera,
        viewport_rect,
        hex_size=HEX_SIZE,
        origin=ORIGIN,
        margin=0,
    )


def test_visible_world_tiles_returns_only_visible_tiles() -> None:
    camera = Camera()
    viewport_rect = pygame.Rect(0, 0, 400, 300)
    tiles = [(0, 0), (10, 10), (1, 0)]

    result = visible_world_tiles(
        tiles,
        camera,
        viewport_rect,
        hex_size=HEX_SIZE,
        origin=ORIGIN,
    )

    assert result == [(0, 0), (1, 0)]


def test_visible_world_tiles_preserves_input_order() -> None:
    camera = Camera()
    viewport_rect = pygame.Rect(0, 0, 400, 300)
    tiles = [(1, 0), (10, 10), (0, 0)]

    result = visible_world_tiles(
        tiles,
        camera,
        viewport_rect,
        hex_size=HEX_SIZE,
        origin=ORIGIN,
    )

    assert result == [(1, 0), (0, 0)]


def test_visible_world_tiles_returns_empty_list_for_empty_input() -> None:
    result = visible_world_tiles(
        [],
        Camera(),
        pygame.Rect(0, 0, 400, 300),
        hex_size=HEX_SIZE,
        origin=ORIGIN,
    )

    assert result == []


def test_visibility_query_does_not_modify_original_tiles() -> None:
    camera = Camera()
    viewport_rect = pygame.Rect(0, 0, 400, 300)
    tiles = [(0, 0), (10, 10), (1, 0)]
    original_tiles = tiles.copy()

    visible_world_tiles(
        tiles,
        camera,
        viewport_rect,
        hex_size=HEX_SIZE,
        origin=ORIGIN,
    )

    assert tiles == original_tiles


def test_visibility_supports_negative_camera_offset() -> None:
    camera = Camera()
    camera.offset_x = -50
    camera.offset_y = -100
    viewport_rect = pygame.Rect(0, 0, 100, 100)

    assert tile_is_in_viewport(
        (0, 0),
        camera,
        viewport_rect,
        hex_size=HEX_SIZE,
        origin=ORIGIN,
        margin=0,
    )


def test_large_world_corner_is_visible_when_camera_centers_on_it() -> None:
    camera = Camera()
    viewport_rect = pygame.Rect(20, 78, 900, 600)
    tile = (21, 15)
    world_pos = axial_to_world_pixel(tile, HEX_SIZE, ORIGIN)
    camera.center_on(world_pos, viewport_rect)

    assert tile_is_in_viewport(
        tile,
        camera,
        viewport_rect,
        hex_size=HEX_SIZE,
        origin=ORIGIN,
    )


def test_visibility_query_does_not_move_camera() -> None:
    camera = Camera()
    camera.offset_x = -125.5
    camera.offset_y = 32.25
    offsets_before = (camera.offset_x, camera.offset_y)

    tile_is_in_viewport(
        (2, 3),
        camera,
        pygame.Rect(0, 0, 400, 300),
        hex_size=HEX_SIZE,
        origin=ORIGIN,
    )

    assert (camera.offset_x, camera.offset_y) == offsets_before
