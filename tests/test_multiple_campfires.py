from main import Game, CAMP_POSITION


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