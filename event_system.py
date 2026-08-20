"""Daily event logic for Stone Age Survival.

This module contains pure game logic and must not depend on pygame.
"""

import random
from dataclasses import dataclass

from constants import (
    EVENT_CAVE,
    EVENT_MIGRATION,
    EVENT_NONE,
    EVENT_STORM,
    EVENT_WOLF_TRACKS,
)


@dataclass(frozen=True)
class DailyEvent:
    """Represents one event affecting the current day or night."""

    event_type: str
    title: str
    description: str


EVENT_DATA: dict[str, tuple[str, str]] = {
    EVENT_NONE: (
        "Quiet Day",
        "No unusual activity is expected today.",
    ),
    EVENT_STORM: (
        "Storm Approaching",
        "A storm is coming tonight. The campfire will consume extra fuel.",
    ),
    EVENT_WOLF_TRACKS: (
        "Wolf Tracks",
        "Fresh wolf tracks were found. More wolves may attack tonight.",
    ),
    EVENT_MIGRATION: (
        "Animal Migration",
        "A nearby animal migration provides extra food today.",
    ),
    EVENT_CAVE: (
        "Cave Discovery",
        "A nearby cave contains useful stone resources.",
    ),
}


def create_daily_event(event_type: str) -> DailyEvent:
    """Create a DailyEvent from a valid event type."""

    if event_type not in EVENT_DATA:
        raise ValueError(f"Unknown event type: {event_type}")

    title, description = EVENT_DATA[event_type]

    return DailyEvent(
        event_type=event_type,
        title=title,
        description=description,
    )


def generate_daily_event(
    day: int,
    rng: random.Random,
) -> DailyEvent:
    """Generate one reproducible daily event.

    The random generator must be supplied by the caller so tests and game
    sessions can reproduce the same sequence when required.
    """

    if day < 1:
        raise ValueError("Day must be at least 1.")

    event_types = (
        EVENT_NONE,
        EVENT_STORM,
        EVENT_WOLF_TRACKS,
        EVENT_MIGRATION,
        EVENT_CAVE,
    )

    event_type = rng.choice(event_types)

    return create_daily_event(event_type)


def is_night_event(event_type: str) -> bool:
    """Return True if the event directly changes the upcoming night."""

    if event_type not in EVENT_DATA:
        raise ValueError(f"Unknown event type: {event_type}")

    return event_type in {
        EVENT_STORM,
        EVENT_WOLF_TRACKS,
    }


def get_night_forecast(event: DailyEvent) -> str:
    """Return a short forecast message suitable for the game UI."""

    if event.event_type == EVENT_STORM:
        return "Storm tonight: campfire fuel use increased."

    if event.event_type == EVENT_WOLF_TRACKS:
        return "Wolf activity tonight: expect more wolves."

    return "Tonight: normal conditions."