from __future__ import annotations

import math


def axial_to_world_pixel(
    position: tuple[int, int],
    hex_size: float,
    origin: tuple[float, float] = (0.0, 0.0),
) -> tuple[float, float]:
    """
    Convert axial hex coordinates (q, r) into world-pixel coordinates.

    This function does not know anything about:
    - camera
    - HUD
    - fullscreen
    - pygame display

    The returned coordinates belong to the game world.
    """
    q, r = position
    origin_x, origin_y = origin

    x = (
        origin_x
        + hex_size
        * math.sqrt(3)
        * (q + r / 2)
    )

    y = (
        origin_y
        + hex_size
        * 1.5
        * r
    )

    return x, y


def world_to_axial_nearest(
    world_pos: tuple[float, float],
    hex_size: float,
    cols: int,
    rows: int,
    origin: tuple[float, float] = (0.0, 0.0),
) -> tuple[int, int] | None:
    """
    Return the valid hex whose center is closest to world_pos.

    This intentionally uses the same nearest-center approach as the
    existing game implementation so behaviour stays compatible.
    """
    world_x, world_y = world_pos

    best_tile: tuple[int, int] | None = None
    best_distance = hex_size * 1.05

    for r in range(rows):
        for q in range(cols):
            tile = (q, r)

            center_x, center_y = axial_to_world_pixel(
                tile,
                hex_size,
                origin,
            )

            distance = math.hypot(
                world_x - center_x,
                world_y - center_y,
            )

            if distance < best_distance:
                best_distance = distance
                best_tile = tile

    return best_tile