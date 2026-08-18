"""Tests for the daily event subsystem."""

import random

import pytest

from constants import (
    EVENT_CAVE,
    EVENT_MIGRATION,
    EVENT_NONE,
    EVENT_STORM,
    EVENT_WOLF_TRACKS,
)
from event_system import (
    DailyEvent,
    create_daily_event,
    generate_daily_event,
    get_night_forecast,
    is_night_event,
)


def test_create_none_event():
    event = create_daily_event(EVENT_NONE)

    assert isinstance(event, DailyEvent)
    assert event.event_type == EVENT_NONE
    assert event.title == "Quiet Day"
    assert event.description


def test_create_storm_event():
    event = create_daily_event(EVENT_STORM)

    assert event.event_type == EVENT_STORM
    assert "Storm" in event.title
    assert "fuel" in event.description.lower()


def test_create_wolf_tracks_event():
    event = create_daily_event(EVENT_WOLF_TRACKS)

    assert event.event_type == EVENT_WOLF_TRACKS
    assert "Wolf" in event.title
    assert "wolves" in event.description.lower()


def test_create_migration_event():
    event = create_daily_event(EVENT_MIGRATION)

    assert event.event_type == EVENT_MIGRATION
    assert "Migration" in event.title
    assert "food" in event.description.lower()


def test_create_cave_event():
    event = create_daily_event(EVENT_CAVE)

    assert event.event_type == EVENT_CAVE
    assert "Cave" in event.title
    assert "stone" in event.description.lower()


def test_invalid_event_type_raises_value_error():
    with pytest.raises(ValueError):
        create_daily_event("meteor")


def test_generate_event_returns_valid_event():
    rng = random.Random(123)

    event = generate_daily_event(1, rng)

    assert event.event_type in {
        EVENT_NONE,
        EVENT_STORM,
        EVENT_WOLF_TRACKS,
        EVENT_MIGRATION,
        EVENT_CAVE,
    }


def test_seeded_generation_is_reproducible():
    rng_a = random.Random(42)
    rng_b = random.Random(42)

    sequence_a = [
        generate_daily_event(day, rng_a).event_type
        for day in range(1, 11)
    ]

    sequence_b = [
        generate_daily_event(day, rng_b).event_type
        for day in range(1, 11)
    ]

    assert sequence_a == sequence_b


def test_invalid_day_raises_value_error():
    rng = random.Random(1)

    with pytest.raises(ValueError):
        generate_daily_event(0, rng)


def test_night_event_detection():
    assert is_night_event(EVENT_STORM) is True
    assert is_night_event(EVENT_WOLF_TRACKS) is True
    assert is_night_event(EVENT_NONE) is False
    assert is_night_event(EVENT_MIGRATION) is False
    assert is_night_event(EVENT_CAVE) is False


def test_invalid_night_event_check_raises_value_error():
    with pytest.raises(ValueError):
        is_night_event("invalid")


def test_storm_forecast():
    event = create_daily_event(EVENT_STORM)

    forecast = get_night_forecast(event)

    assert "Storm" in forecast
    assert "fuel" in forecast.lower()


def test_wolf_tracks_forecast():
    event = create_daily_event(EVENT_WOLF_TRACKS)

    forecast = get_night_forecast(event)

    assert "Wolf" in forecast
    assert "more wolves" in forecast.lower()


def test_non_night_event_uses_normal_forecast():
    for event_type in (
        EVENT_NONE,
        EVENT_MIGRATION,
        EVENT_CAVE,
    ):
        event = create_daily_event(event_type)

        assert get_night_forecast(event) == "Tonight: normal conditions."