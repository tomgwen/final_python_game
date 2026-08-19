from main import Game


def test_finish_night_keeps_player_position():
    game = Game()

    original_position = (3, 3)
    game.player = original_position
    game.selected_tile = original_position
    game.phase = "night"
    game.night_turns_left = 1

    old_day = game.day

    game.finish_night()

    assert game.player == original_position
    assert game.selected_tile == original_position
    assert game.day == old_day + 1
    assert game.phase == "day"