from constants import (
    ENEMY_BEAR,
    ENEMY_BOAR,
    ENEMY_HYENA,
    ENEMY_SABERTOOTH,
    ENEMY_WOLF,
)
from enemy import (
    available_enemy_types,
    claim_loot,
    create_enemy,
    damage_enemy,
    get_enemy_max_health,
    get_enemy_name,
    get_enemy_start_day,
)


def test_create_hyena():
    enemy = create_enemy(ENEMY_HYENA, (1, 1))

    assert enemy.enemy_type == ENEMY_HYENA
    assert enemy.health == 40
    assert enemy.damage == 8
    assert enemy.move_range == 2
    assert enemy.fear_of_fire is True


def test_create_bear():
    enemy = create_enemy(ENEMY_BEAR, (1, 1))

    assert enemy.health == 90
    assert enemy.damage == 16
    assert enemy.move_range == 1
    assert enemy.fear_of_fire is False


def test_create_sabertooth():
    enemy = create_enemy(ENEMY_SABERTOOTH, (1, 1))

    assert enemy.health == 70
    assert enemy.damage == 18
    assert enemy.move_range == 2
    assert enemy.fear_of_fire is False


def test_enemy_names():
    assert get_enemy_name(ENEMY_WOLF) == "狼"
    assert get_enemy_name(ENEMY_BOAR) == "野豬"
    assert get_enemy_name(ENEMY_HYENA) == "鬣狗"
    assert get_enemy_name(ENEMY_BEAR) == "熊"
    assert get_enemy_name(ENEMY_SABERTOOTH) == "劍齒虎"


def test_enemy_max_health():
    assert get_enemy_max_health(ENEMY_WOLF) == 30
    assert get_enemy_max_health(ENEMY_BOAR) == 55
    assert get_enemy_max_health(ENEMY_HYENA) == 40
    assert get_enemy_max_health(ENEMY_BEAR) == 90
    assert get_enemy_max_health(ENEMY_SABERTOOTH) == 70


def test_enemy_unlock_days():
    assert get_enemy_start_day(ENEMY_WOLF) == 1
    assert get_enemy_start_day(ENEMY_BOAR) == 2
    assert get_enemy_start_day(ENEMY_HYENA) == 4
    assert get_enemy_start_day(ENEMY_BEAR) == 6
    assert get_enemy_start_day(ENEMY_SABERTOOTH) == 9


def test_day_one_only_has_wolf():
    assert available_enemy_types(1) == [ENEMY_WOLF]


def test_day_two_unlocks_boar():
    assert set(available_enemy_types(2)) == {
        ENEMY_WOLF,
        ENEMY_BOAR,
    }


def test_day_four_unlocks_hyena():
    assert ENEMY_HYENA in available_enemy_types(4)
    assert ENEMY_BEAR not in available_enemy_types(4)


def test_day_six_unlocks_bear():
    assert ENEMY_BEAR in available_enemy_types(6)
    assert ENEMY_SABERTOOTH not in available_enemy_types(6)


def test_day_nine_unlocks_all_enemy_types():
    assert set(available_enemy_types(9)) == {
        ENEMY_WOLF,
        ENEMY_BOAR,
        ENEMY_HYENA,
        ENEMY_BEAR,
        ENEMY_SABERTOOTH,
    }


def test_hyena_loot():
    enemy = create_enemy(ENEMY_HYENA, (0, 0))
    damage_enemy(enemy, enemy.health)

    assert claim_loot(enemy) == {
        "hide": 1,
        "food": 1,
    }


def test_bear_loot():
    enemy = create_enemy(ENEMY_BEAR, (0, 0))
    damage_enemy(enemy, enemy.health)

    assert claim_loot(enemy) == {
        "hide": 2,
        "food": 2,
    }


def test_sabertooth_loot():
    enemy = create_enemy(ENEMY_SABERTOOTH, (0, 0))
    damage_enemy(enemy, enemy.health)

    assert claim_loot(enemy) == {
        "hide": 2,
        "food": 2,
    }
def test_enemy_wall_damage():
    from enemy import get_enemy_wall_damage

    assert get_enemy_wall_damage(ENEMY_WOLF) == 10
    assert get_enemy_wall_damage(ENEMY_BOAR) == 25
    assert get_enemy_wall_damage(ENEMY_HYENA) == 12
    assert get_enemy_wall_damage(ENEMY_BEAR) == 30
    assert get_enemy_wall_damage(ENEMY_SABERTOOTH) == 22
from main import Game


def enemy_types_in_game(game: Game) -> set[str]:
    return {
        enemy.enemy_type
        for enemy in game.enemies
    }


def test_day_one_spawns_only_wolves():
    game = Game()
    game.day = 1

    game.spawn_enemies()

    assert enemy_types_in_game(game) == {
        ENEMY_WOLF,
    }


def test_day_two_spawns_boars():
    game = Game()
    game.day = 2

    game.spawn_enemies()

    types = enemy_types_in_game(game)

    assert ENEMY_WOLF in types
    assert ENEMY_BOAR in types
    assert ENEMY_HYENA not in types


def test_day_four_spawns_hyenas():
    game = Game()
    game.day = 4

    game.spawn_enemies()

    types = enemy_types_in_game(game)

    assert ENEMY_HYENA in types
    assert ENEMY_BEAR not in types


def test_day_six_spawns_bears():
    game = Game()
    game.day = 6

    game.spawn_enemies()

    types = enemy_types_in_game(game)

    assert ENEMY_BEAR in types
    assert ENEMY_SABERTOOTH not in types


def test_day_nine_spawns_sabertooth():
    game = Game()
    game.day = 9

    game.spawn_enemies()

    assert ENEMY_SABERTOOTH in enemy_types_in_game(game)
def test_spawned_enemy_types_respect_unlock_day():
    for day in range(1, 10):
        game = Game()
        game.day = day

        game.spawn_enemies()

        allowed = set(available_enemy_types(day))

        assert all(
            enemy.enemy_type in allowed
            for enemy in game.enemies
        )
def test_new_enemy_max_health_matches_created_enemy():
    for enemy_type in (
        ENEMY_WOLF,
        ENEMY_BOAR,
        ENEMY_HYENA,
        ENEMY_BEAR,
        ENEMY_SABERTOOTH,
    ):
        enemy = create_enemy(enemy_type, (0, 0))

        assert enemy.health == get_enemy_max_health(enemy_type)