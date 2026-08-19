"""Windowed, resizable, and fullscreen display management."""

from __future__ import annotations

import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class DisplayManager:
    def __init__(self) -> None:
        self.fullscreen = False
        self.windowed_size = (SCREEN_WIDTH, SCREEN_HEIGHT)

    def create_window(self) -> pygame.Surface:
        return pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)

    def toggle_fullscreen(self) -> pygame.Surface:
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        return pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)

    def resize(self, size: tuple[int, int]) -> pygame.Surface:
        if self.fullscreen:
            return pygame.display.get_surface()
        self.windowed_size = (max(960, size[0]), max(540, size[1]))
        return pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)

    def restore(self) -> pygame.Surface:
        """Restore the managed mode after a presentation takes the display."""
        if self.fullscreen:
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        return pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
