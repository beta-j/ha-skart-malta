"""Constants for the Skart Malta integration."""

from __future__ import annotations

from datetime import date, timedelta

DOMAIN = "skart_malta"

# Config / options keys
CONF_NAME = "name"
CONF_COLLECTION_TIME = "collection_time"
CONF_GLASS_WEEKS = "glass_weeks"
CONF_GLASS_WEEKDAY = "glass_weekday"

DEFAULT_NAME = "Skart Malta"
DEFAULT_COLLECTION_TIME = "07:30"
# Which Fridays of the month glass is collected (1 = first, 3 = third).
DEFAULT_GLASS_WEEKS = [1, 3]
# 0 = Monday ... 6 = Sunday. Glass is on Friday by default.
DEFAULT_GLASS_WEEKDAY = 4

# Waste stream identifiers
STREAM_ORGANIC = "organic"
STREAM_MIXED = "mixed"
STREAM_RECYCLABLE = "recyclable"
STREAM_GLASS = "glass"
STREAM_NONE = "none"

# Friendly labels (English + bag colour, matching national scheme)
STREAM_LABELS = {
    STREAM_ORGANIC: "Organic (white bag)",
    STREAM_MIXED: "Mixed (black bag)",
    STREAM_RECYCLABLE: "Recyclable (grey/green bag)",
    STREAM_GLASS: "Glass",
    STREAM_NONE: "No collection",
}

STREAM_ICONS = {
    STREAM_ORGANIC: "mdi:leaf",
    STREAM_MIXED: "mdi:trash-can",
    STREAM_RECYCLABLE: "mdi:recycle",
    STREAM_GLASS: "mdi:bottle-wine",
    STREAM_NONE: "mdi:calendar-blank",
}

# National standardised weekday schedule (since 2 Jan 2023).
# Python weekday(): Monday = 0 ... Sunday = 6.
WEEKDAY_SCHEDULE: dict[int, str] = {
    0: STREAM_ORGANIC,     # Monday
    1: STREAM_MIXED,       # Tuesday
    2: STREAM_ORGANIC,     # Wednesday
    3: STREAM_RECYCLABLE,  # Thursday
    4: STREAM_ORGANIC,     # Friday
    5: STREAM_MIXED,       # Saturday
    6: STREAM_NONE,        # Sunday
}


def _weekday_ordinal(target: date) -> int:
    """Return which occurrence of its weekday a date is within its month (1-based)."""
    return (target.day - 1) // 7 + 1


def is_glass_day(target: date, glass_weekday: int, glass_weeks: list[int]) -> bool:
    """Return True if glass is collected on the given date."""
    if target.weekday() != glass_weekday:
        return False
    return _weekday_ordinal(target) in glass_weeks


def streams_for_date(
    target: date, glass_weekday: int, glass_weeks: list[int]
) -> list[str]:
    """Return all waste streams collected on a given date.

    Glass shares Friday with organic when due, so a date can have
    more than one stream.
    """
    streams: list[str] = []
    base = WEEKDAY_SCHEDULE.get(target.weekday(), STREAM_NONE)
    if base != STREAM_NONE:
        streams.append(base)
    if is_glass_day(target, glass_weekday, glass_weeks):
        streams.append(STREAM_GLASS)
    if not streams:
        streams.append(STREAM_NONE)
    return streams


def next_glass_date(
    start: date, glass_weekday: int, glass_weeks: list[int], horizon: int = 60
) -> date | None:
    """Return the next date (on/after start) on which glass is collected."""
    for offset in range(horizon):
        candidate = start + timedelta(days=offset)
        if is_glass_day(candidate, glass_weekday, glass_weeks):
            return candidate
    return None
