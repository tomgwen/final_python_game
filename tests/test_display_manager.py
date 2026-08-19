import pygame

from display_manager import DisplayManager


def test_resize_tracks_windowed_size(monkeypatch):
    calls = []
    surface = pygame.Surface((1400, 800))
    monkeypatch.setattr(pygame.display, "set_mode", lambda size, flags=0: calls.append((size, flags)) or surface)
    manager = DisplayManager()
    assert manager.resize((1400, 800)) is surface
    assert manager.windowed_size == (1400, 800)
    assert calls[-1][1] & pygame.RESIZABLE


def test_toggle_fullscreen_and_back(monkeypatch):
    calls = []
    surface = pygame.Surface((1280, 720))
    monkeypatch.setattr(pygame.display, "set_mode", lambda size, flags=0: calls.append((size, flags)) or surface)
    manager = DisplayManager()
    manager.toggle_fullscreen()
    assert manager.fullscreen is True
    assert calls[-1][1] & pygame.FULLSCREEN
    manager.toggle_fullscreen()
    assert manager.fullscreen is False
    assert calls[-1][1] & pygame.RESIZABLE
