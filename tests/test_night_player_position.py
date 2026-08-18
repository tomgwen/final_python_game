from main import Game


def test_start_night_keeps_player_position():
    game = Game()

    target = (6, 4)

    # 確保目標格可走。
    game.terrain[target] = "grass"

    game.player = target
    game.selected_tile = target
    game.phase = "day"

    game.start_night()

    assert game.phase == "night"
    assert game.player == target
    assert game.selected_tile == target