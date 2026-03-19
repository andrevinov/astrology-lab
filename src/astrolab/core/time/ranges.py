"""
Time range generation utilities.

This module provides deterministic helpers for generating UTC datetime
sequences with fixed steps.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterator

from astrolab.core.time.jd import ensure_utc


def iter_datetimes(
    start: datetime,
    end: datetime,
    step: timedelta,
    *,
    inclusive: bool = True,
) -> Iterator[datetime]:
    """
    Yield UTC datetimes from start to end using a fixed step.

    All inputs are normalized to UTC using ensure_utc.
    """

    start = ensure_utc(start).dt
    end = ensure_utc(end).dt

    if end < start:
        raise ValueError("end must be greater than or equal to start")

    if step <= timedelta(0):
        raise ValueError("step must be a positive timedelta")

    current = start

    if inclusive:
        while current <= end:
            yield current
            current += step
    else:
        while current < end:
            yield current
            current += step


def iter_hours(
    start: datetime,
    end: datetime,
    *,
    hours: int = 1,
    inclusive: bool = True,
) -> Iterator[datetime]:
    """
    Yield UTC datetimes using an hourly step.
    """

    if hours <= 0:
        raise ValueError("hours must be a positive integer")

    yield from iter_datetimes(
        start=start,
        end=end,
        step=timedelta(hours=hours),
        inclusive=inclusive,
    )


def iter_days(
    start: datetime,
    end: datetime,
    *,
    days: int = 1,
    inclusive: bool = True,
) -> Iterator[datetime]:
    """
    Yield UTC datetimes using a daily step.
    """

    if days <= 0:
        raise ValueError("days must be a positive integer")

    yield from iter_datetimes(
        start=start,
        end=end,
        step=timedelta(days=days),
        inclusive=inclusive,
    )