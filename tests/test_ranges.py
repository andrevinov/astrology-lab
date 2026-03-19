from datetime import datetime, timedelta, timezone

import pytest

from astrolab.core.time.ranges import iter_datetimes, iter_days, iter_hours  # type: ignore


# ---------------------------------------------------------
# Helper: create a UTC datetime quickly
# ---------------------------------------------------------
def dt(hour: int) -> datetime:
    return datetime(2026, 1, 1, hour, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------
# Test 1: basic generator with 1-hour step
# ---------------------------------------------------------
def test_iter_datetimes_basic_hourly() -> None:
    """
    Basic scenario:

    - start: 00h
    - end: 03h
    - step: 1 hour

    Expected: 0, 1, 2, 3 (inclusive)
    """

    result = list(
        iter_datetimes(
            start=dt(0),
            end=dt(3),
            step=timedelta(hours=1),
        )
    )

    assert result == [dt(0), dt(1), dt(2), dt(3)]


# ---------------------------------------------------------
# Test 2: exclusive end (inclusive=False)
# ---------------------------------------------------------
def test_iter_datetimes_exclusive_end() -> None:
    """
    Same scenario, but inclusive=False.

    Expected: stops at 2h (does not include 3h)
    """

    result = list(
        iter_datetimes(
            start=dt(0),
            end=dt(3),
            step=timedelta(hours=1),
            inclusive=False,
        )
    )

    assert result == [dt(0), dt(1), dt(2)]


# ---------------------------------------------------------
# Test 3: step of 2 hours
# ---------------------------------------------------------
def test_iter_datetimes_step_two_hours() -> None:
    """
    Ensures step size is respected.

    step = 2h → 0, 2, 4
    """

    result = list(
        iter_datetimes(
            start=dt(0),
            end=dt(4),
            step=timedelta(hours=2),
        )
    )

    assert result == [dt(0), dt(2), dt(4)]


# ---------------------------------------------------------
# Test 4: iter_hours wrapper
# ---------------------------------------------------------
def test_iter_hours_wrapper() -> None:
    """
    iter_hours should behave as a thin wrapper over iter_datetimes.
    """

    result = list(iter_hours(start=dt(0), end=dt(3)))

    assert result == [dt(0), dt(1), dt(2), dt(3)]


# ---------------------------------------------------------
# Test 5: iter_days wrapper
# ---------------------------------------------------------
def test_iter_days_wrapper() -> None:
    """
    Same concept as iter_hours, but using day steps.
    """

    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 1, 3, tzinfo=timezone.utc)

    result = list(iter_days(start=start, end=end))

    assert result == [
        datetime(2026, 1, 1, tzinfo=timezone.utc),
        datetime(2026, 1, 2, tzinfo=timezone.utc),
        datetime(2026, 1, 3, tzinfo=timezone.utc),
    ]


# ---------------------------------------------------------
# Test 6: generator nature (not a list)
# ---------------------------------------------------------
def test_iter_datetimes_is_generator() -> None:
    """
    Ensures the function returns a generator (lazy iterator),
    not a precomputed list.
    """

    gen = iter_datetimes(
        start=dt(0),
        end=dt(1),
        step=timedelta(hours=1),
    )

    assert hasattr(gen, "__iter__")
    assert hasattr(gen, "__next__")


# ---------------------------------------------------------
# Test 7: invalid step (<= 0)
# ---------------------------------------------------------
def test_iter_datetimes_invalid_step() -> None:
    """
    Step must be strictly positive.
    """

    with pytest.raises(ValueError):
        list(
            iter_datetimes(
                start=dt(0),
                end=dt(1),
                step=timedelta(0),
            )
        )


# ---------------------------------------------------------
# Test 8: invalid range (end < start)
# ---------------------------------------------------------
def test_iter_datetimes_invalid_range() -> None:
    """
    End must be greater than or equal to start.
    """

    with pytest.raises(ValueError):
        list(
            iter_datetimes(
                start=dt(2),
                end=dt(1),
                step=timedelta(hours=1),
            )
        )


# ---------------------------------------------------------
# Test 9: requires UTC-aware datetime
# ---------------------------------------------------------
def test_iter_datetimes_requires_utc() -> None:
    """
    Naive datetime should raise an error.
    """

    naive = datetime(2026, 1, 1, 0, 0, 0)

    with pytest.raises(ValueError):
        list(
            iter_datetimes(
                start=naive,
                end=naive,
                step=timedelta(hours=1),
            )
        )