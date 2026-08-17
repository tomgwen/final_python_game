"""Campfire fuel system for Stone Age Survival."""

from constants import CAMPFIRE_MAX_FUEL, RESOURCE_WOOD
from inventory import Inventory


STARTING_FUEL = 3
FUEL_PER_WOOD = 2
RELIGHT_FUEL = 2


class Campfire:
    """Represent the permanent campfire at the player's camp."""

    def __init__(self, position: tuple[int, int]) -> None:
        """Create a lit campfire with its initial fuel."""
        self.position = position
        self.fuel = STARTING_FUEL
        self.lit = True

    def add_fuel(
        self,
        inventory: Inventory,
        amount: int = 1,
    ) -> bool:
        """Spend wood and add fuel to a currently lit campfire.

        One wood adds two fuel. Fuel is capped at CAMPFIRE_MAX_FUEL.
        Extra fuel above the maximum may be wasted.
        """
        if amount < 0:
            raise ValueError("Fuel amount cannot be negative.")

        if amount == 0:
            return False

        if not self.lit:
            return False

        if not inventory.spend({RESOURCE_WOOD: amount}):
            return False

        self.fuel = min(
            CAMPFIRE_MAX_FUEL,
            self.fuel + amount * FUEL_PER_WOOD,
        )
        return True

    def consume(self, amount: int = 1) -> None:
        """Consume campfire fuel.

        The fire is extinguished automatically when fuel reaches zero.
        """
        if amount < 0:
            raise ValueError("Fuel consumption cannot be negative.")

        if amount == 0:
            return

        self.fuel = max(0, self.fuel - amount)

        if self.fuel == 0:
            self.lit = False

    def relight(self, inventory: Inventory) -> bool:
        """Relight an extinguished fire using one wood."""
        if self.lit:
            return False

        if not inventory.spend({RESOURCE_WOOD: 1}):
            return False

        self.fuel = RELIGHT_FUEL
        self.lit = True
        return True

    def get_light_radius(self) -> int:
        """Return the current campfire light radius."""
        if not self.lit or self.fuel == 0:
            return 0

        if self.fuel <= 3:
            return 1

        if self.fuel <= 7:
            return 2

        return 3