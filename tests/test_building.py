from building import BuildingManager
from constants import (
    BUILD_TRAP,
    BUILD_WALL,
    TRAP_MAX_HP,
    WALL_MAX_HP,
)
from inventory import Inventory


def test_build_wall_success():
    inventory = Inventory()
    manager = BuildingManager()

    assert manager.build(BUILD_WALL, (2, 3), inventory) is True

    wall = manager.get_building((2, 3))

    assert wall is not None
    assert wall.building_type == BUILD_WALL
    assert wall.hp == WALL_MAX_HP
    assert wall.max_hp == WALL_MAX_HP
    assert wall.active is True
    assert inventory.get("wood") == 2


def test_build_trap_success():
    inventory = Inventory()
    manager = BuildingManager()

    assert manager.build(BUILD_TRAP, (4, 5), inventory) is True

    trap = manager.get_building((4, 5))

    assert trap is not None
    assert trap.building_type == BUILD_TRAP
    assert trap.hp == TRAP_MAX_HP
    assert trap.max_hp == TRAP_MAX_HP
    assert trap.active is True
    assert inventory.get("wood") == 3
    assert inventory.get("stone") == 1


def test_cannot_build_on_occupied_position():
    inventory = Inventory()
    manager = BuildingManager()

    assert manager.build(BUILD_WALL, (1, 1), inventory) is True

    wood_before = inventory.get("wood")

    assert manager.build(BUILD_TRAP, (1, 1), inventory) is False
    assert inventory.get("wood") == wood_before


def test_build_fails_without_resources():
    inventory = Inventory()
    manager = BuildingManager()

    inventory.spend({"wood": 5})

    assert manager.build(BUILD_WALL, (1, 1), inventory) is False
    assert manager.get_building((1, 1)) is None


def test_unknown_building_type_raises_value_error():
    inventory = Inventory()
    manager = BuildingManager()

    try:
        manager.build("unknown", (1, 1), inventory)
        assert False
    except ValueError:
        pass


def test_damage_wall():
    inventory = Inventory()
    manager = BuildingManager()

    manager.build(BUILD_WALL, (2, 2), inventory)

    assert manager.damage_building((2, 2), 20) is True

    wall = manager.get_building((2, 2))

    assert wall is not None
    assert wall.hp == WALL_MAX_HP - 20


def test_wall_removed_when_hp_reaches_zero():
    inventory = Inventory()
    manager = BuildingManager()

    manager.build(BUILD_WALL, (2, 2), inventory)

    assert manager.damage_building((2, 2), WALL_MAX_HP) is True
    assert manager.get_building((2, 2)) is None


def test_trap_cannot_be_damaged():
    inventory = Inventory()
    manager = BuildingManager()

    manager.build(BUILD_TRAP, (3, 3), inventory)

    assert manager.damage_building((3, 3), 1) is False
    assert manager.get_building((3, 3)) is not None


def test_negative_damage_raises_value_error():
    inventory = Inventory()
    manager = BuildingManager()

    manager.build(BUILD_WALL, (2, 2), inventory)

    try:
        manager.damage_building((2, 2), -1)
        assert False
    except ValueError:
        pass


def test_trigger_trap_marks_it_inactive_and_keeps_it():
    inventory = Inventory()
    manager = BuildingManager()

    manager.build(BUILD_TRAP, (5, 5), inventory)

    assert manager.trigger_trap((5, 5)) is True

    trap = manager.get_building((5, 5))

    assert trap is not None
    assert trap.building_type == BUILD_TRAP
    assert trap.active is False


def test_inactive_trap_cannot_trigger_again():
    inventory = Inventory()
    manager = BuildingManager()

    manager.build(BUILD_TRAP, (5, 5), inventory)

    assert manager.trigger_trap((5, 5)) is True
    assert manager.trigger_trap((5, 5)) is False

    trap = manager.get_building((5, 5))

    assert trap is not None
    assert trap.active is False


def test_triggering_non_trap_returns_false():
    inventory = Inventory()
    manager = BuildingManager()

    manager.build(BUILD_WALL, (5, 5), inventory)

    assert manager.trigger_trap((5, 5)) is False
    assert manager.get_building((5, 5)) is not None