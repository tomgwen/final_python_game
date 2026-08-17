"""Campfire system for Stone Age Survival."""

from inventory import Inventory


CAMPFIRE_COST = {
    "wood": 4,
    "stone": 2,
}


class Campfire:
    """Represent a campfire that provides warmth and healing."""

    def __init__(self, position: tuple[int, int]) -> None:
        """Initialize a campfire at the given position."""
        self.position = position
        self.is_lit = False

    def light(self, inventory: Inventory) -> bool:
        """Light the campfire if the required resources are available."""
        if self.is_lit:
            return False

        if not inventory.spend(CAMPFIRE_COST):
            return False

        self.is_lit = True
        return True

    def extinguish(self) -> None:
        """Extinguish the campfire."""
        self.is_lit = False

    def can_heal(self) -> bool:
        """Return whether the campfire is currently lit."""
        return self.is_lit

    def heal_amount(self) -> int:
        """Return the amount of health restored by the campfire."""
        if not self.is_lit:
            return 0

        return 10