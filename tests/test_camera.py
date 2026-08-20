import pygame

from camera import Camera


def test_camera_starts_with_zero_offset():
    camera = Camera()

    assert camera.offset_x == 0.0
    assert camera.offset_y == 0.0


def test_world_to_screen_with_zero_offset():
    camera = Camera()

    screen_pos = camera.world_to_screen((100, 200))

    assert screen_pos == (100, 200)


def test_world_to_screen_applies_camera_offset():
    camera = Camera()
    camera.offset_x = -50
    camera.offset_y = 25

    screen_pos = camera.world_to_screen((100, 200))

    assert screen_pos == (50, 225)


def test_screen_to_world_reverses_camera_offset():
    camera = Camera()
    camera.offset_x = -50
    camera.offset_y = 25

    world_pos = camera.screen_to_world((50, 225))

    assert world_pos == (100, 200)


def test_world_screen_round_trip():
    camera = Camera()
    camera.offset_x = -325
    camera.offset_y = 140

    original_world_pos = (920, 610)

    screen_pos = camera.world_to_screen(original_world_pos)
    restored_world_pos = camera.screen_to_world(screen_pos)

    assert restored_world_pos == original_world_pos


def test_center_on_places_world_position_at_viewport_center():
    camera = Camera()

    viewport = pygame.Rect(
        0,
        0,
        1000,
        700,
    )

    player_world_pos = (800, 600)

    camera.center_on(
        player_world_pos,
        viewport,
    )

    player_screen_pos = camera.world_to_screen(
        player_world_pos
    )

    assert player_screen_pos == (
        viewport.centerx,
        viewport.centery,
    )


def test_center_on_respects_viewport_position():
    camera = Camera()

    viewport = pygame.Rect(
        40,
        80,
        900,
        600,
    )

    target_world_pos = (1000, 700)

    camera.center_on(
        target_world_pos,
        viewport,
    )

    target_screen_pos = camera.world_to_screen(
        target_world_pos
    )

    assert target_screen_pos == (
        viewport.centerx,
        viewport.centery,
    )


def test_reset_clears_camera_offset():
    camera = Camera()

    camera.offset_x = -500
    camera.offset_y = 300

    camera.reset()

    assert camera.offset_x == 0.0
    assert camera.offset_y == 0.0