from main import Game, CAMP_POSITION, neighbors


def in_map_neighbors(game: Game, tile: tuple[int, int]) -> set[tuple[int, int]]:
    return {
        neighbor
        for neighbor in neighbors(tile)
        if neighbor in game.terrain
    }


def test_initial_exploration_only_reveals_camp_area():
    game = Game()

    expected = {CAMP_POSITION}
    expected.update(in_map_neighbors(game, CAMP_POSITION))

    assert game.discovered == expected
    assert len(game.discovered) < len(game.terrain)


def test_discovered_tiles_are_always_inside_map():
    game = Game()

    assert all(tile in game.terrain for tile in game.discovered)


def test_day_movement_reveals_target_and_neighbors():
    game = Game()

    target = next(
        tile
        for tile in neighbors(game.player)
        if tile in game.terrain and game.terrain[tile] != "water"
    )

    assert game.move_to(target) is True

    assert target in game.discovered

    for neighbor in in_map_neighbors(game, target):
        assert neighbor in game.discovered


def test_reveal_around_never_adds_out_of_bounds_tiles():
    game = Game()

    corner = (0, 0)
    game.reveal_around(corner)

    assert all(tile in game.terrain for tile in game.discovered)