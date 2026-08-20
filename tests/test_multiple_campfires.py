from main import Game, CAMP_POSITION
from main import Game, CAMP_POSITION, hex_distance
from campfire import Campfire
from enemy import create_enemy
from constants import ENEMY_WOLF, ENEMY_BOAR
from main import Game, CAMP_POSITION, hex_distance, neighbors

def test_game_starts_with_one_primary_campfire():
    game = Game()

    assert len(game.campfires) == 1
    assert CAMP_POSITION in game.campfires


def test_legacy_campfire_reference_matches_primary_campfire():
    game = Game()

    assert game.campfire is game.campfires[CAMP_POSITION]


def test_campfire_at_returns_primary_campfire():
    game = Game()

    assert game.campfire_at(CAMP_POSITION) is game.campfire


def test_lit_campfires_contains_primary_campfire():
    game = Game()

    assert game.campfire in game.lit_campfires()
def test_player_is_near_primary_campfire_when_at_camp():
    game = Game()

    game.player = CAMP_POSITION

    assert game.is_near_campfire(game.campfire) is True


def test_player_is_near_primary_campfire_when_adjacent():
    game = Game()

    adjacent = next(
        tile
        for tile in game.terrain
        if tile != CAMP_POSITION
        and abs(tile[0] - CAMP_POSITION[0]) <= 1
        and abs(tile[1] - CAMP_POSITION[1]) <= 1
        and tile in game.terrain
        and __import__("main").hex_distance(tile, CAMP_POSITION) == 1
    )

    game.player = adjacent

    assert game.is_near_campfire(game.campfire) is True


def test_player_is_not_near_campfire_when_far_away():
    game = Game()

    far_tile = next(
        tile
        for tile in game.terrain
        if __import__("main").hex_distance(tile, CAMP_POSITION) > 1
    )

    game.player = far_tile

    assert game.is_near_campfire(game.campfire) is False
def get_valid_campfire_build_tile(game: Game) -> tuple[int, int]:
    for tile in game.terrain:
        if (
            tile != CAMP_POSITION
            and game.terrain[tile] != "water"
            and hex_distance(game.player, tile) <= 2
            and game.campfire_at(tile) is None
            and game.buildings.get_building(tile) is None
            and game.treasure_chest_at(tile) is None
        ):
            game.discovered.add(tile)
            return tile

    raise AssertionError("No valid campfire build tile found")


def test_can_build_second_campfire():
    game = Game()
    tile = get_valid_campfire_build_tile(game)

    assert game.can_build_campfire_at(tile) is True


def test_build_campfire_costs_resources_and_adds_fire():
    game = Game()
    tile = get_valid_campfire_build_tile(game)

    game.inventory.add("wood", 3)
    game.inventory.add("stone", 2)

    wood_before = game.inventory.get("wood")
    stone_before = game.inventory.get("stone")
    turns_before = game.day_turns_left

    assert game.build_campfire_at(tile) is True

    assert game.campfire_at(tile) is not None
    assert game.inventory.get("wood") == wood_before - 3
    assert game.inventory.get("stone") == stone_before - 2
    assert game.day_turns_left == turns_before - 1


def test_cannot_build_two_campfires_on_same_tile():
    game = Game()
    tile = get_valid_campfire_build_tile(game)

    game.inventory.add("wood", 6)
    game.inventory.add("stone", 4)

    assert game.build_campfire_at(tile) is True
    assert game.build_campfire_at(tile) is False

    assert len(game.campfires) == 2


def test_cannot_build_campfire_on_water():
    game = Game()

    water_tile = next(
        tile
        for tile, terrain in game.terrain.items()
        if terrain == "water"
    )

    game.discovered.add(water_tile)
    game.player = water_tile

    assert game.can_build_campfire_at(water_tile) is False
def test_cannot_build_wall_or_trap_on_campfire_tile():
    game = Game()
    tile = get_valid_campfire_build_tile(game)

    game.inventory.add("wood", 6)
    game.inventory.add("stone", 4)

    assert game.build_campfire_at(tile) is True

    assert game.campfire_at(tile) is not None
    assert game.can_build_at(tile) is False

def test_can_refuel_specific_second_campfire():
    game = Game()

    second_position = next(
        tile
        for tile in game.terrain
        if tile != CAMP_POSITION
        and hex_distance(tile, CAMP_POSITION) == 1
        and game.terrain[tile] != "water"
    )

    second = Campfire(second_position)
    second.fuel = 3
    game.campfires[second_position] = second

    game.player = second_position
    game.inventory.add("wood", 1)

    primary_fuel_before = game.campfire.fuel

    assert game.add_firewood_day(second) is True

    assert second.fuel == 6
    assert game.campfire.fuel == primary_fuel_before


def test_cannot_refuel_specific_campfire_from_far_away():
    game = Game()

    second_position = next(
        tile
        for tile in game.terrain
        if hex_distance(tile, CAMP_POSITION) > 2
        and game.terrain[tile] != "water"
    )
    second = Campfire(second_position)
    second.fuel = 3
    game.campfires[second_position] = second

    game.player = CAMP_POSITION
    game.inventory.add("wood", 1)

    wood_before = game.inventory.get("wood")
    turns_before = game.day_turns_left

    assert game.add_firewood_day(second) is False

    assert second.fuel == 3
    assert game.inventory.get("wood") == wood_before
    assert game.day_turns_left == turns_before

def test_all_campfires_consume_fuel_each_night_turn():
    game = Game()

    second_position = next(
        tile
        for tile in game.terrain
        if tile != CAMP_POSITION
        and game.terrain[tile] != "water"
    )

    second = Campfire(second_position)
    game.campfires[second_position] = second

    game.phase = "night"
    game.night_turns_left = 20

    primary_before = game.campfire.fuel
    second_before = second.fuel

    # 避免測試因為沒有敵人而提前結束夜晚。
    game.enemy_phase = lambda: None
    game.apply_campfire_night_effects = lambda: None
    game.alive_enemies = lambda: [object()]
    game.advance_night_turn()

    assert game.campfire.fuel == primary_before - 1
    assert second.fuel == second_before - 1


def test_one_campfire_can_extinguish_without_affecting_another():
    game = Game()

    second_position = next(
        tile
        for tile in game.terrain
        if tile != CAMP_POSITION
        and game.terrain[tile] != "water"
    )

    second = Campfire(second_position)
    game.campfires[second_position] = second

    game.campfire.fuel = 1
    game.campfire.lit = True

    second.fuel = 3
    second.lit = True

    game.phase = "night"
    game.night_turns_left = 20

    game.enemy_phase = lambda: None
    game.apply_campfire_night_effects = lambda: None
    game.alive_enemies = lambda: [object()]

    game.advance_night_turn()

    assert game.campfire.fuel == 0
    assert game.campfire.lit is False

    assert second.fuel == 2
    assert second.lit is True
def test_tile_inside_lit_campfire_radius_four_is_safe():
    game = Game()

    tile = next(
        tile
        for tile in game.terrain
        if hex_distance(tile, CAMP_POSITION) == 4
    )

    assert game.is_in_lit_campfire_range(tile) is True


def test_tile_outside_lit_campfire_radius_four_is_not_safe():
    game = Game()

    tile = next(
        tile
        for tile in game.terrain
        if hex_distance(tile, CAMP_POSITION) > 4
    )

    assert game.is_in_lit_campfire_range(tile) is False


def test_extinguished_campfire_does_not_provide_safe_range():
    game = Game()

    game.campfire.lit = False
    game.campfire.fuel = 0

    assert game.is_in_lit_campfire_range(CAMP_POSITION) is False


def test_second_lit_campfire_also_provides_safe_range():
    game = Game()

    second_position = next(
        tile
        for tile in game.terrain
        if hex_distance(tile, CAMP_POSITION) > 4
        and game.terrain[tile] != "water"
    )

    second = Campfire(second_position)
    game.campfires[second_position] = second

    assert game.is_in_lit_campfire_range(second_position) is True
def test_enemy_inside_lit_campfire_range_takes_two_damage():
    game = Game()
    game.spawn_enemies()

    enemy = game.enemies[0]
    enemy.position = CAMP_POSITION

    health_before = enemy.health

    game.apply_campfire_night_effects()

    assert enemy.health == health_before - 2
def find_wolf_test_position(game: Game) -> tuple[int, int]:
    for tile in game.terrain:
        if game.terrain[tile] == "water":
            continue

        if hex_distance(tile, CAMP_POSITION) != 5:
            continue

        closer_tiles = [
            neighbor
            for neighbor in __import__("main").neighbors(tile)
            if neighbor in game.terrain
            and game.terrain[neighbor] != "water"
            and hex_distance(neighbor, CAMP_POSITION) == 4
        ]

        if closer_tiles:
            return tile

    raise AssertionError("No suitable wolf test position found")


def test_wolf_will_not_enter_lit_campfire_radius():
    game = Game()

    start = find_wolf_test_position(game)
    wolf = create_enemy(ENEMY_WOLF, start)

    moved = game.enemy_step(wolf)

    assert moved is False
    assert wolf.position == start


def test_wolf_can_approach_when_campfire_is_extinguished():
    game = Game()

    start = find_wolf_test_position(game)
    wolf = create_enemy(ENEMY_WOLF, start)

    game.campfire.lit = False
    game.campfire.fuel = 0

    moved = game.enemy_step(wolf)

    assert moved is True
    assert hex_distance(wolf.position, CAMP_POSITION) == 4
def test_player_can_attack_enemy_away_from_primary_campfire():
    game = Game()
    game.phase = "night"

    player_tile = next(
        tile
        for tile in game.terrain
        if hex_distance(tile, CAMP_POSITION) > 4
        and game.terrain[tile] != "water"
    )

    enemy_tile = next(
        tile
        for tile in neighbors(player_tile)
        if tile in game.terrain
        and game.terrain[tile] != "water"
    )

    game.player = player_tile

    enemy = create_enemy(ENEMY_WOLF, enemy_tile)
    game.enemies = [enemy]

    assert game.attack_enemy_at(enemy_tile) is True
    assert game.attack_enemy is enemy
    assert game.attack_animating is True