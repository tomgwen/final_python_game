"""Building system for Stone Age Survival."""

from dataclasses import dataclass

from constants import (
    BUILD_TRAP,
    BUILD_WALL,
    TRAP_MAX_HP,
    WALL_MAX_HP,
)
from inventory import Inventory


WALL_COST = {"wood": 3}
TRAP_COST = {"wood": 2, "stone": 1}


@dataclass
class Building:
    """Represent a building placed on the map."""

    building_type: str
    position: tuple[int, int]
    hp: int
    max_hp: int
    active: bool = True


class BuildingManager:
    """Manage buildings placed at map positions."""

    def __init__(self) -> None:
        """Initialize an empty building collection."""
        self.buildings: dict[tuple[int, int], Building] = {}

    def _get_cost(self, building_type: str) -> dict[str, int]:
        """Return the resource cost for a building type."""
        if building_type == BUILD_WALL:
            return WALL_COST.copy()

        if building_type == BUILD_TRAP:
            return TRAP_COST.copy()

        raise ValueError(f"Unknown building type: {building_type}")

    def can_build(self, position: tuple[int, int]) -> bool:
        """Return whether a building can be placed at the position."""
        return position not in self.buildings

    def build(
        self,
        building_type: str,
        position: tuple[int, int],
        inventory: Inventory,
    ) -> bool:
        """Build a structure if the position is free and resources exist."""
        cost = self._get_cost(building_type)

        if not self.can_build(position):
            return False

        if not inventory.spend(cost):
            return False

        if building_type == BUILD_WALL:
            building = Building(
                building_type=BUILD_WALL,
                position=position,
                hp=WALL_MAX_HP,
                max_hp=WALL_MAX_HP,
                active=True,
            )
        else:
            building = Building(
                building_type=BUILD_TRAP,
                position=position,
                hp=TRAP_MAX_HP,
                max_hp=TRAP_MAX_HP,
                active=True,
            )

        self.buildings[position] = building
        return True

    def get_building(
        self,
        position: tuple[int, int],
    ) -> Building | None:
        """Return the building at a position, or None."""
        return self.buildings.get(position)

    def damage_building(
        self,
        position: tuple[int, int],
        damage: int,
    ) -> bool:
        """Damage a wall and remove it when its HP reaches zero."""
        if damage < 0:
            raise ValueError("Damage cannot be negative.")

        building = self.get_building(position)

        if building is None:
            return False

        if building.building_type != BUILD_WALL:
            return False

        building.hp = max(0, building.hp - damage)

        if building.hp == 0:
            del self.buildings[position]

        return True

    def trigger_trap(self, position: tuple[int, int]) -> bool:
        """Trigger an active trap without removing it from the map."""
        building = self.get_building(position)

        if building is None:
            return False

        if building.building_type != BUILD_TRAP:
            return False

        if not building.active:
            return False

        building.active = False
        return True