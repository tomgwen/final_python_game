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


def play_day_survived(
    day_number: int,
    screen: pygame.Surface | None = None,
    display_manager=None,
) -> None:
    """Show a short, dismissible overlay for the day that just ended."""

    if day_number < 1:
        raise ValueError("day_number must be at least 1")

    pygame.init()

    # 單獨執行 day_transition.py 時才自己建立視窗。
    # 從 main.py 進來時直接沿用目前的 fullscreen / windowed surface。
    if screen is None:
        screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.RESIZABLE,
        )

    pygame.display.set_caption("石器時代：荒野求生 - 黎明")

    clock = pygame.time.Clock()

    title_font = _font(58, True)
    body_font = _font(27)
    prompt_font = _font(17)

    start_time = pygame.time.get_ticks()

    running = True

    while running:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - start_time

        if elapsed >= DISPLAY_DURATION_MS:
            break

        # =====================================================
        # 事件處理
        # =====================================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.VIDEORESIZE:
                if display_manager is not None:
                    screen = display_manager.resize(event.size)
                else:
                    screen = pygame.display.set_mode(
                        event.size,
                        pygame.RESIZABLE,
                    )
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    if display_manager is not None:
                        screen = display_manager.toggle_fullscreen()
                    continue

                if event.key in (
                    pygame.K_SPACE,
                    pygame.K_RETURN,
                    pygame.K_ESCAPE,
                ):
                    running = False
                    continue

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                running = False
                continue

        # =====================================================
        # 目前真正的畫面尺寸
        # =====================================================
        width, height = screen.get_size()

        center_x = width // 2
        center_y = height // 2

        # =====================================================
        # 黎明背景
        # =====================================================
        progress = min(
            1.0,
            elapsed / 700,
        )

        dawn = int(
            18 + 70 * progress
        )

        screen.fill(
            (
                dawn,
                int(dawn * 0.78),
                int(dawn * 0.48),
            )
        )

        # =====================================================
        # 下方日出光暈
        # =====================================================
        glow = pygame.Surface(
            (width, height),
            pygame.SRCALPHA,
        )

        glow_radius = max(
            430,
            int(min(width, height) * 0.42),
        )

        pygame.draw.circle(
            glow,
            (
                255,
                196,
                94,
                int(120 * progress),
            ),
            (
                center_x,
                height + int(glow_radius * 0.1),
            ),
            glow_radius,
        )

        screen.blit(
            glow,
            (0, 0),
        )

        # =====================================================
        # 文字
        # =====================================================
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
            "Space / 左鍵繼續  |  F11 全螢幕  |  Esc 關閉",
            True,
            (225, 218, 198),
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    center_x,
                    center_y - 35,
                )
            ),
        )

        screen.blit(
            body,
            body.get_rect(
                center=(
                    center_x,
                    center_y + 35,
                )
            ),
        )

        screen.blit(
            prompt,
            prompt.get_rect(
                center=(
                    center_x,
                    height - 65,
                )
            ),
        )

        pygame.display.flip()
        clock.tick(FPS)