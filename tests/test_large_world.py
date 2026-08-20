from constants import CAMP_POSITION, MAP_COLS, MAP_ROWS
from main import Game, create_world


def test_large_world_dimensions():
    assert MAP_COLS == 22
    assert MAP_ROWS == 16


def test_large_world_has_expected_tile_count():
    terrain, resources = create_world()

    expected_tiles = MAP_COLS * MAP_ROWS

    assert len(terrain) == expected_tiles
    assert len(resources) == expected_tiles


def test_all_world_positions_are_inside_bounds():
    terrain, resources = create_world()

    for q, r in terrain:
        assert 0 <= q < MAP_COLS
        assert 0 <= r < MAP_ROWS

    for q, r in resources:
        assert 0 <= q < MAP_COLS
        assert 0 <= r < MAP_ROWS


def test_camp_position_stays_valid():
    q, r = CAMP_POSITION

    assert 0 <= q < MAP_COLS
    assert 0 <= r < MAP_ROWS


def test_camp_tile_is_grass():
    terrain, _ = create_world()

    assert terrain[CAMP_POSITION] == "grass"


def test_non_water_tiles_start_with_six_resources():
    terrain, resources = create_world()

    for tile, terrain_type in terrain.items():
        if terrain_type == "water":
            assert resources[tile] == 0
        else:
            assert resources[tile] == 6


def test_new_game_contains_full_large_world():
    game = Game()

    assert len(game.terrain) == MAP_COLS * MAP_ROWS
    assert len(game.resources) == MAP_COLS * MAP_ROWS