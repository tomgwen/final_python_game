"""Presentation-only overlay shown after the player survives a night."""

from __future__ import annotations

import os

import pygame

from constants import FPS, SCREEN_HEIGHT, SCREEN_WIDTH


DISPLAY_DURATION_MS = 1800


def _font(size: int, bold: bool = False) -> pygame.font.Font:
    font_path = None

    for path in (
        r"C:\Windows\Fonts\msjh.ttc",
        r"C:\Windows\Fonts\msjhbd.ttc",
        r"C:\Windows\Fonts\mingliu.ttc",
    ):
        if os.path.exists(path):
            font_path = path
            break

    if font_path is None:
        font_path = pygame.font.match_font(
            "Microsoft JhengHei, Noto Sans CJK TC"
        )

    font = (
        pygame.font.Font(font_path, size)
        if font_path
        else pygame.font.Font(None, size)
    )
    font.set_bold(bold)

    return font


def play_day_survived(day_number: int) -> None:
    """Show a short, dismissible overlay for the day that just ended."""
    if day_number < 1:
        raise ValueError("day_number must be at least 1")

    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("石器時代：荒野求生 - 黎明")

    clock = pygame.time.Clock()

    title_font = _font(58, True)
    body_font = _font(27)
    prompt_font = _font(17)

    start_time = pygame.time.get_ticks()

    running = True

    while running:
        elapsed = pygame.time.get_ticks() - start_time

        if elapsed >= DISPLAY_DURATION_MS:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and event.key in (
                pygame.K_SPACE,
                pygame.K_RETURN,
                pygame.K_ESCAPE,
            ):
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                running = False

        progress = min(1.0, elapsed / 700)

        dawn = int(18 + 70 * progress)

        screen.fill(
            (
                dawn,
                int(dawn * 0.78),
                int(dawn * 0.48),
            )
        )

        glow = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SRCALPHA,
        )

        pygame.draw.circle(
            glow,
            (255, 196, 94, int(120 * progress)),
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT + 40),
            430,
        )

        screen.blit(glow, (0, 0))

        title = title_font.render(
            f"DAY {day_number} SURVIVED",
            True,
            (255, 239, 201),
        )

        body = body_font.render(
            f"第 {day_number} 天生存成功",
            True,
            (255, 214, 132),
        )

        prompt = prompt_font.render(
            "Space / 左鍵繼續  |  Esc 關閉",
            True,
            (225, 218, 198),
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 35,
                )
            ),
        )

        screen.blit(
            body,
            body.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 35,
                )
            ),
        )

        screen.blit(
            prompt,
            prompt.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT - 65,
                )
            ),
        )

        pygame.display.flip()
        clock.tick(FPS)