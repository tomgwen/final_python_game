import pygame

from ui_layout import get_game_viewport, get_right_hud_rect


def test_layout_does_not_overlap_at_supported_sizes():
    for size in ((1280, 720), (1920, 1080)):
        screen = pygame.Surface(size)
        viewport = get_game_viewport(screen)
        hud = get_right_hud_rect(screen)
        assert not viewport.colliderect(hud)
        assert hud.width < viewport.width


def test_viewport_grows_with_screen_width():
    small = get_game_viewport(pygame.Surface((1280, 720)))
    large = get_game_viewport(pygame.Surface((1920, 1080)))
    assert large.width > small.width
