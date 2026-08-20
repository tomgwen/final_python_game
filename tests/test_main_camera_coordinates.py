import pygame

from camera import Camera
from main import (
    HEX_SIZE,
    MAP_ORIGIN_X,
    MAP_ORIGIN_Y,
    axial_to_pixel,
    tile_at_pixel,
)


def test_axial_to_pixel_without_camera_keeps_original_behavior():
    tile = (5, 4)

    pixel = axial_to_pixel(tile)

    assert isinstance(pixel[0], int)
    assert isinstance(pixel[1], int)


def test_axial_to_pixel_with_camera_applies_offset():
    camera = Camera()
    camera.offset_x = -100
    camera.offset_y = 50

    original = axial_to_pixel((5, 4))
    shifted = axial_to_pixel((5, 4), camera)

    assert shifted == (
        original[0] - 100,
        original[1] + 50,
    )


def test_tile_at_pixel_without_camera_still_finds_tile():
    tile = (5, 4)

    pixel = axial_to_pixel(tile)

    result = tile_at_pixel(pixel)

    assert result == tile


def test_tile_at_pixel_with_camera_finds_shifted_tile():
    camera = Camera()
    camera.offset_x = -120
    camera.offset_y = -60

    viewport = pygame.Rect(
        0,
        0,
        1280,
        720,
    )

    tile = (5, 4)

    screen_pixel = axial_to_pixel(
        tile,
        camera,
    )

    result = tile_at_pixel(
        screen_pixel,
        camera,
        viewport,
    )

    assert result == tile


def test_camera_round_trip_works_for_large_world_tile():
    camera = Camera()

    viewport = pygame.Rect(
        20,
        78,
        1000,
        600,
    )

    tile = (18, 12)

    world_pixel = axial_to_pixel(tile)

    camera.center_on(
        world_pixel,
        viewport,
    )

    screen_pixel = axial_to_pixel(
        tile,
        camera,
    )

    result = tile_at_pixel(
        screen_pixel,
        camera,
        viewport,
    )

    assert result == tile


def test_tile_outside_viewport_returns_none():
    camera = Camera()

    viewport = pygame.Rect(
        100,
        100,
        500,
        400,
    )

    result = tile_at_pixel(
        (20, 20),
        camera,
        viewport,
    )

    assert result is None