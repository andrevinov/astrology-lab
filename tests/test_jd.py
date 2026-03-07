# tests/test_jd.py
#
# Unit tests for src/astrolab/core/time/jd.py
#
# What are we testing here?
# This module is responsible for the time-layer foundation:
# - enforcing UTC-aware datetimes
# - rejecting naive datetimes
# - making UTC explicit through a small wrapper
#
# At this stage, Julian Day conversion itself is intentionally not implemented
# in this module, because that responsibility belongs to the ephemeris layer.
# So we also test that the placeholder functions fail in the expected way.

from datetime import datetime, timedelta, timezone

import pytest

from src.astrolab.core.time.jd import (
    UTCDateTime,
    datetime_to_jd_ut,
    ensure_utc,
    jd_ut_to_datetime,
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
# Placeholder conversion functions
# ==========================================================

def test_datetime_to_jd_ut_raises_not_implemented():
    """
    datetime_to_jd_ut is intentionally not implemented in core/time/jd.py.

    This test protects the architectural decision that Julian Day conversion
    belongs to the ephemeris layer, not the pure core time layer.
    """
    dt = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)

    with pytest.raises(NotImplementedError, match="Use ephemeris"):
        datetime_to_jd_ut(dt)


def test_jd_ut_to_datetime_raises_not_implemented():
    """
    jd_ut_to_datetime is also intentionally left unimplemented here.

    The goal is to keep this module free from Swiss Ephemeris dependencies.
    """
    with pytest.raises(NotImplementedError, match="Use ephemeris"):
        jd_ut_to_datetime(2460000.5)