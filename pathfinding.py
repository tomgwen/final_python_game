"""Hex-grid pathfinding utilities for Stone Age Survival."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable

from constants import MAP_COLS, MAP_ROWS


HEX_DIRECTIONS = (
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
)


def is_valid_position(
    position: tuple[int, int],
    cols: int = MAP_COLS,
    rows: int = MAP_ROWS,
) -> bool:
    """Return whether an axial hex coordinate is inside the map."""
    q, r = position

    return (
        0 <= q < cols
        and 0 <= r < rows
    )


def get_hex_neighbors(
    position: tuple[int, int],
    cols: int = MAP_COLS,
    rows: int = MAP_ROWS,
) -> list[tuple[int, int]]:
    """Return valid neighboring axial hex coordinates."""
    q, r = position

    result: list[tuple[int, int]] = []

    for dq, dr in HEX_DIRECTIONS:
        candidate = (
            q + dq,
            r + dr,
        )

        if is_valid_position(
            candidate,
            cols,
            rows,
        ):
            result.append(candidate)

    return result


def find_hex_path(
    start: tuple[int, int],
    goal: tuple[int, int],
    is_walkable: Callable[[tuple[int, int]], bool],
    blocked: set[tuple[int, int]] | None = None,
    cols: int = MAP_COLS,
    rows: int = MAP_ROWS,
) -> list[tuple[int, int]] | None:
    """Find the shortest valid path using BFS.

    The returned path includes both ``start`` and ``goal``.

    Example:
        [(5, 4), (6, 4), (7, 4)]

    means the movement cost is 2 turns.

    ``blocked`` is intended for temporary obstacles such as enemies.
    """

    if not is_valid_position(start, cols, rows):
        return None

    if not is_valid_position(goal, cols, rows):
        return None

    if start == goal:
        return [start]

    blocked_tiles = set(
        blocked or set()
    )

    # The player is allowed to begin on a position that may have
    # become temporarily blocked.
    blocked_tiles.discard(start)

    if goal in blocked_tiles:
        return None

    if not is_walkable(goal):
        return None

    queue: deque[tuple[int, int]] = deque(
        [start]
    )

    previous: dict[
        tuple[int, int],
        tuple[int, int] | None,
    ] = {
        start: None
    }

    while queue:
        current = queue.popleft()

        for neighbor in get_hex_neighbors(
            current,
            cols,
            rows,
        ):
            if neighbor in previous:
                continue

            if neighbor in blocked_tiles:
                continue

            if not is_walkable(neighbor):
                continue

            previous[neighbor] = current

            if neighbor == goal:
                path = [goal]
                cursor = current

                while cursor is not None:
                    path.append(cursor)
                    cursor = previous[cursor]

                path.reverse()
                return path

            queue.append(neighbor)

    return None