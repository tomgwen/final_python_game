from constants import MAX_HEALTH
from survival import SurvivalStats


def test_low_hunger_restores_two_health():
    stats = SurvivalStats()
    stats.health = 90
    stats.hunger = 10

    change = stats.apply_hunger_health_effect()

    assert stats.health == 92
    assert change == 2


def test_low_hunger_does_not_exceed_max_health():
    stats = SurvivalStats()
    stats.health = MAX_HEALTH - 1
    stats.hunger = 10

    change = stats.apply_hunger_health_effect()

    assert stats.health == MAX_HEALTH
    assert change == 1


def test_hunger_20_to_60_does_not_change_health():
    stats = SurvivalStats()

    for hunger in (20, 40, 60):
        stats.health = 90
        stats.hunger = hunger

        change = stats.apply_hunger_health_effect()

        assert stats.health == 90
        assert change == 0


def test_hunger_61_to_79_loses_one_health():
    stats = SurvivalStats()
    stats.health = 90
    stats.hunger = 61

    change = stats.apply_hunger_health_effect()

    assert stats.health == 89
    assert change == -1


def test_hunger_80_to_99_loses_two_health():
    stats = SurvivalStats()
    stats.health = 90
    stats.hunger = 80

    change = stats.apply_hunger_health_effect()

    assert stats.health == 88
    assert change == -2


def test_hunger_100_loses_three_health():
    stats = SurvivalStats()
    stats.health = 90
    stats.hunger = 100

    change = stats.apply_hunger_health_effect()

    assert stats.health == 87
    assert change == -3


def test_health_never_goes_below_zero():
    stats = SurvivalStats()
    stats.health = 2
    stats.hunger = 100

    change = stats.apply_hunger_health_effect()

    assert stats.health == 0
    assert change == -2


def test_daily_hunger_only_increases_hunger():
    stats = SurvivalStats()
    stats.health = 50
    stats.hunger = 70

    stats.apply_daily_hunger()

    assert stats.hunger == 85
    assert stats.health == 50