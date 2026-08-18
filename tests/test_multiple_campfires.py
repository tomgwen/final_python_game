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