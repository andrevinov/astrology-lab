# tests/test_jd.py
#
# Unit tests for src/astrolab/core/time/jd.py
#
# What are we testing here?
# This module is responsible for the time-layer foundation:
# - enforcing UTC-aware datetimes
# - rejecting naive datetimes
# - making UTC explicit through a small wrapper
# - defining reusable UTC search windows for scanners and event search
#
# At this stage, Julian Day conversion itself does not belong here.
# That responsibility lives in the ephemeris layer.

from datetime import datetime, timedelta, timezone

import pytest

from src.astrolab.core.time.jd import (
    SearchWindow,
    UTCDateTime,
    ensure_utc,
)


# ==========================================================
# UTCDateTime
# ==========================================================

def test_utcdatetime_accepts_explicit_utc_datetime():
    """
    UTCDateTime should accept an aware datetime
    whose tzinfo is exactly timezone.utc.
    """
    dt = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)

    wrapped = UTCDateTime(dt)

    assert wrapped.dt == dt


def test_utcdatetime_rejects_naive_datetime():
    """
    UTCDateTime must reject naive datetimes.

    A naive datetime has no timezone information, which makes it unsafe
    for astronomical calculations.
    """
    dt = datetime(2026, 2, 1, 12, 0, 0)

    with pytest.raises(ValueError, match="aware datetime"):
        UTCDateTime(dt)


def test_utcdatetime_rejects_non_utc_timezone():
    """
    UTCDateTime must reject aware datetimes that are not explicitly UTC.

    This is a deliberate design decision:
    the wrapper exists to make UTC-ness explicit and strict.
    """
    utc_plus_3 = timezone(timedelta(hours=3))
    dt = datetime(2026, 2, 1, 12, 0, 0, tzinfo=utc_plus_3)

    with pytest.raises(ValueError, match="timezone.utc"):
        UTCDateTime(dt)


# ==========================================================
# ensure_utc
# ==========================================================

def test_ensure_utc_rejects_naive_datetime():
    """
    ensure_utc should reject naive datetimes,
    because timezone conversion is impossible without tzinfo.
    """
    dt = datetime(2026, 2, 1, 12, 0, 0)

    with pytest.raises(ValueError, match="timezone-aware"):
        ensure_utc(dt)


def test_ensure_utc_keeps_utc_datetime_unchanged():
    """
    If the input datetime is already UTC-aware,
    ensure_utc should return a UTCDateTime wrapper
    containing the same instant.
    """
    dt = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)

    wrapped = ensure_utc(dt)

    assert isinstance(wrapped, UTCDateTime)
    assert wrapped.dt == dt
    assert wrapped.dt.tzinfo == timezone.utc


def test_ensure_utc_converts_other_timezone_to_utc():
    """
    If the input datetime is timezone-aware but not UTC,
    ensure_utc should convert it to UTC before wrapping it.

    Example:
    15:00 at UTC+3 == 12:00 UTC
    """
    utc_plus_3 = timezone(timedelta(hours=3))
    dt = datetime(2026, 2, 1, 15, 0, 0, tzinfo=utc_plus_3)

    wrapped = ensure_utc(dt)

    expected = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)

    assert isinstance(wrapped, UTCDateTime)
    assert wrapped.dt == expected
    assert wrapped.dt.tzinfo == timezone.utc


# ==========================================================
# SearchWindow
# ==========================================================

def test_searchwindow_accepts_valid_utc_range():
    """
    SearchWindow should accept two aware UTC datetimes
    when start_utc < end_utc.
    """
    start = datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2026, 2, 2, 0, 0, 0, tzinfo=timezone.utc)

    window = SearchWindow(start_utc=start, end_utc=end)

    assert window.start_utc == start
    assert window.end_utc == end


def test_searchwindow_rejects_naive_datetimes():
    """
    SearchWindow must reject naive datetimes.
    """
    start = datetime(2026, 2, 1, 0, 0, 0)
    end = datetime(2026, 2, 2, 0, 0, 0, tzinfo=timezone.utc)

    with pytest.raises(ValueError, match="aware datetimes"):
        SearchWindow(start_utc=start, end_utc=end)


def test_searchwindow_rejects_non_utc_timezone():
    """
    SearchWindow must reject aware datetimes that are not timezone.utc.
    """
    utc_plus_3 = timezone(timedelta(hours=3))
    start = datetime(2026, 2, 1, 0, 0, 0, tzinfo=utc_plus_3)
    end = datetime(2026, 2, 2, 0, 0, 0, tzinfo=timezone.utc)

    with pytest.raises(ValueError, match="timezone.utc"):
        SearchWindow(start_utc=start, end_utc=end)


def test_searchwindow_requires_start_before_end():
    """
    SearchWindow requires start_utc < end_utc.
    """
    t = datetime(2026, 2, 1, 0, 0, 0, tzinfo=timezone.utc)

    with pytest.raises(ValueError, match="start_utc < end_utc"):
        SearchWindow(start_utc=t, end_utc=t)