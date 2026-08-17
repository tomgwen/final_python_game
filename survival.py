"""Player survival statistics for Stone Age Survival."""

from constants import MAX_ARMOR, MAX_HEALTH, MAX_HUNGER
from inventory import Inventory


class SurvivalStats:
    """Track the player's health, armor, and hunger."""

    def __init__(self) -> None:
        """Initialize the player's survival statistics."""
        self.health: int = MAX_HEALTH
        self.armor: int = 0
        self.hunger: int = 20

    def take_damage(self, amount: int) -> int:
        """Apply damage to armor first and return actual health loss."""
        if amount < 0:
            raise ValueError("Damage cannot be negative.")

        armor_damage = min(self.armor, amount)
        self.armor -= armor_damage

        health_damage = amount - armor_damage
        self.health = max(0, self.health - health_damage)

        return health_damage

    def add_armor(self, amount: int) -> None:
        """Increase armor up to the maximum armor value."""
        if amount < 0:
            raise ValueError("Armor amount cannot be negative.")

        self.armor = min(MAX_ARMOR, self.armor + amount)

    def increase_hunger(self, amount: int) -> None:
        """Increase hunger up to the maximum hunger value."""
        if amount < 0:
            raise ValueError("Hunger amount cannot be negative.")

        self.hunger = min(MAX_HUNGER, self.hunger + amount)

    def eat(self, inventory: Inventory, amount: int = 1) -> bool:
        """Consume food and reduce hunger."""
        if amount < 0:
            raise ValueError("Food amount cannot be negative.")

        if amount == 0:
            return False

        if inventory.get("food") < amount:
            return False

        inventory.spend({"food": amount})
        self.hunger = max(0, self.hunger - amount * 25)

        return True

    def apply_daily_hunger(self) -> None:
        """Increase daily hunger and apply starvation damage if necessary."""
        self.hunger = min(MAX_HUNGER, self.hunger + 15)

        if self.hunger >= 80:
            self.health = max(0, self.health - 10)

    def is_dead(self) -> bool:
        """Return True when the player's health reaches zero."""
        return self.health <= 0