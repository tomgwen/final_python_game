"""Responsive layout helpers for the game viewport and right-side HUD."""

from __future__ import annotations

import pygame


OUTER_MARGIN = 20
TOP_OFFSET = 78
BOTTOM_MARGIN = 20
GAP = 16
HUD_RATIO = 0.20
MIN_HUD_WIDTH = 180


def get_right_hud_rect(screen: pygame.Surface) -> pygame.Rect:
    """Return the compact right HUD rectangle for the current display size."""
    width, height = screen.get_size()
    hud_width = max(MIN_HUD_WIDTH, int(width * HUD_RATIO) - OUTER_MARGIN)
    return pygame.Rect(
        width - OUTER_MARGIN - hud_width,
        TOP_OFFSET,
        hud_width,
        max(1, height - TOP_OFFSET - BOTTOM_MARGIN),
    )


def get_game_viewport(screen: pygame.Surface) -> pygame.Rect:
    """Return the main game viewport without overlapping the HUD."""
    hud = get_right_hud_rect(screen)
    return pygame.Rect(
        OUTER_MARGIN,
        TOP_OFFSET,
        max(1, hud.left - GAP - OUTER_MARGIN),
        max(1, screen.get_height() - TOP_OFFSET - BOTTOM_MARGIN),
    )
