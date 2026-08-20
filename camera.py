from __future__ import annotations


class Camera:
    """
    Handles conversion between world-pixel coordinates and screen coordinates.

    The camera itself does not know anything about:
    - hex tiles
    - HUD size
    - fullscreen
    - map dimensions

    It only works with pixel coordinates and a viewport rectangle.
    """

    def __init__(self) -> None:
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0

    def world_to_screen(
        self,
        world_pos: tuple[float, float],
    ) -> tuple[float, float]:
        """
        Convert a world-pixel position into a screen-pixel position.
        """
        world_x, world_y = world_pos

        return (
            world_x + self.offset_x,
            world_y + self.offset_y,
        )

    def screen_to_world(
        self,
        screen_pos: tuple[float, float],
    ) -> tuple[float, float]:
        """
        Convert a screen-pixel position back into world-pixel coordinates.
        """
        screen_x, screen_y = screen_pos

        return (
            screen_x - self.offset_x,
            screen_y - self.offset_y,
        )

    def center_on(
        self,
        world_pos: tuple[float, float],
        viewport_rect,
    ) -> None:
        """
        Move the camera so world_pos appears at the center
        of the supplied viewport rectangle.
        """
        world_x, world_y = world_pos

        self.offset_x = viewport_rect.centerx - world_x
        self.offset_y = viewport_rect.centery - world_y

    def reset(self) -> None:
        """
        Reset the camera to no offset.
        """
        self.offset_x = 0.0
        self.offset_y = 0.0