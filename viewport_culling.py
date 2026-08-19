from __future__ import annotations

from collections.abc import Iterable

import pygame

from hex_coordinates import axial_to_world_pixel


def tile_is_in_viewport(
    tile: tuple[int, int],
    camera,
    viewport_rect: pygame.Rect,
    *,
    hex_size: float,
    origin: tuple[float, float],
    margin: float = 40.0,
) -> bool:
    """Return whether a tile center is within the expanded viewport."""
    world_pos = axial_to_world_pixel(tile, hex_size, origin)
    screen_pos = camera.world_to_screen(world_pos)
    expanded_viewport = viewport_rect.inflate(
        int(margin * 2),
        int(margin * 2),
    )
    return expanded_viewport.collidepoint(screen_pos)


def visible_world_tiles(
    tiles: Iterable[tuple[int, int]],
    camera,
    viewport_rect: pygame.Rect,
    *,
    hex_size: float,
    origin: tuple[float, float],
    margin: float = 40.0,
) -> list[tuple[int, int]]:
    """Return visible tiles while preserving the caller's iteration order."""
    return [
        tile
        for tile in tiles
        if tile_is_in_viewport(
            tile,
            camera,
            viewport_rect,
            hex_size=hex_size,
            origin=origin,
            margin=margin,
        )
    ]
