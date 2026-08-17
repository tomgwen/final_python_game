"""Inventory system for Stone Age Survival."""

from constants import (
    RESOURCE_FOOD,
    RESOURCE_HIDE,
    RESOURCE_STONE,
    RESOURCE_WOOD,
)


class Inventory:
    """Store and manage the player's shared resources."""

    _VALID_RESOURCES = {
        RESOURCE_FOOD,
        RESOURCE_WOOD,
        RESOURCE_STONE,
        RESOURCE_HIDE,
    }

    def __init__(self) -> None:
        """Initialize the inventory with the default resources."""
        self.resources: dict[str, int] = {
            RESOURCE_FOOD: 3,
            RESOURCE_WOOD: 5,
            RESOURCE_STONE: 2,
            RESOURCE_HIDE: 0,
        }

    def _validate_resource(self, resource: str) -> None:
        """Validate a resource name."""
        if resource not in self._VALID_RESOURCES:
            raise ValueError(f"Unknown resource: {resource}")

    def _validate_cost(self, cost: dict[str, int]) -> None:
        """Validate resource names and amounts in a cost."""
        for resource, amount in cost.items():
            self._validate_resource(resource)

            if amount < 0:
                raise ValueError(
                    "Resource amount cannot be negative."
                )

    def get(self, resource: str) -> int:
        """Return the current amount of a resource."""
        self._validate_resource(resource)
        return self.resources[resource]

    def add(self, resource: str, amount: int) -> None:
        """Add resources to the inventory."""
        self._validate_resource(resource)

        if amount < 0:
            raise ValueError(
                "Resource amount cannot be negative."
            )

        self.resources[resource] += amount

    def has(self, cost: dict[str, int]) -> bool:
        """Return whether the inventory can afford a cost."""
        self._validate_cost(cost)

        return all(
            self.resources[resource] >= amount
            for resource, amount in cost.items()
        )

    def spend(self, cost: dict[str, int]) -> bool:
        """Spend resources atomically if enough resources exist."""
        self._validate_cost(cost)

        if not self.has(cost):
            return False

        for resource, amount in cost.items():
            self.resources[resource] -= amount

        return True