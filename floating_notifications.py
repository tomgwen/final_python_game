"""Presentation-only floating notifications for recent Game log messages."""

from __future__ import annotations

import pygame


class FloatingNotification:
    def __init__(self, text: str, created_at: int, duration_ms: int = 3500):
        self.text = text
        self.created_at = created_at
        self.duration_ms = duration_ms


class FloatingNotificationManager:
    """Keep and draw at most four temporary notification messages."""

    def __init__(self, max_items: int = 4) -> None:
        self.max_items = max_items
        self.notifications: list[FloatingNotification] = []
        self._seen_logs: list[str] = []

    def add(self, text: str, now_ms: int | None = None) -> None:
        if not text:
            return
        created_at = pygame.time.get_ticks() if now_ms is None else now_ms
        self.notifications.append(FloatingNotification(text, created_at))
        self.notifications = self.notifications[-self.max_items :]

    def sync_from_logs(self, logs: list[str], now_ms: int | None = None) -> None:
        """Add only messages newly appended to the rolling Game log."""
        overlap = 0
        max_overlap = min(len(self._seen_logs), len(logs))
        for size in range(max_overlap, -1, -1):
            if self._seen_logs[-size:] == logs[:size] if size else True:
                overlap = size
                break
        for message in logs[overlap:]:
            self.add(message, now_ms)
        self._seen_logs = list(logs)

    def update(self, now_ms: int) -> None:
        self.notifications = [
            item
            for item in self.notifications
            if now_ms - item.created_at < item.duration_ms
        ]

    def draw(
        self,
        screen: pygame.Surface,
        fonts: dict[str, pygame.font.Font],
        viewport_rect: pygame.Rect,
        now_ms: int | None = None,
    ) -> None:
        now = pygame.time.get_ticks() if now_ms is None else now_ms
        y = viewport_rect.bottom - 24
        for item in reversed(self.notifications):
            age = now - item.created_at
            remaining = item.duration_ms - age
            alpha = 255 if remaining >= 1000 else max(0, int(255 * remaining / 1000))
            rendered = fonts["small"].render(item.text, True, (239, 235, 221))
            box = pygame.Surface((min(rendered.get_width() + 24, viewport_rect.width - 24), 32), pygame.SRCALPHA)
            box.fill((18, 20, 22, min(210, alpha)))
            rendered.set_alpha(alpha)
            box.blit(rendered, (12, 6))
            y -= box.get_height() + 7
            screen.blit(box, (viewport_rect.x + 12, y))
