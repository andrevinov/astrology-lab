# tests/test_swe_adapter.py
#
# Unit tests for src/astrolab/ephemeris/swe_adapter.py
#
# What are we testing here?
# This module is our bridge to Swiss Ephemeris.
# At this stage, we want to validate three things:
#
# 1. Time conversion works correctly:
#    - UTC datetime -> Julian Day (UT)
#    - Julian Day (UT) -> UTC datetime
#
# 2. The adapter enforces UTC explicitly where required.
#
# 3. Planetary longitude calculation returns values in the expected shape
#    and range, without yet overcommitting to exact astronomical reference values.
#
# Why avoid asserting an exact Saturn longitude here?
# Because this test file should validate adapter behavior first.
# Exact historical reproduction is better tested later in case-oriented tests.

from datetime import datetime, timezone

import pytest
import swisseph as swe  # type: ignore

from src.astrolab.domain.bodies import Body  # type: ignore
from src.astrolab.ephemeris.swe_adapter import (
    calc_ecl_lon_ut,
    datetime_to_jd_ut,
    jd_ut_to_datetime,
    set_ephe_path,
)


# ==========================================================
# set_ephe_path
# ==========================================================

def test_set_ephe_path_accepts_none():
    """
    The adapter should allow set_ephe_path(None).

    This means:
    - the caller does not explicitly provide ephemeris files
    - Swiss Ephemeris may still work depending on flags/mode
    - the call itself should not fail
    """
    set_ephe_path(None)


# ==========================================================
# datetime_to_jd_ut
# ==========================================================

def test_datetime_to_jd_ut_rejects_non_utc_datetime():
    """
    datetime_to_jd_ut should reject datetimes that are not explicitly UTC.

    This is stricter than merely accepting timezone-aware input:
    the adapter requires timezone.utc specifically.
    """
    dt = datetime(2026, 2, 1, 12, 0, 0)

    with pytest.raises(ValueError, match="UTC datetime"):
        datetime_to_jd_ut(dt)


def test_datetime_to_jd_ut_known_reference_j2000():
    """
    Astronomical reference test.

    J2000.0 corresponds to:
    2000-01-01 12:00:00 UTC -> JD 2451545.0

    This is one of the most standard sanity checks for Julian Day conversion.
    """
    dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    jd = datetime_to_jd_ut(dt)

    assert jd == pytest.approx(2451545.0, abs=1e-9)


def test_datetime_to_jd_ut_known_reference_midnight():
    """
    Another common Julian Day sanity check.

    2000-01-01 00:00:00 UTC -> JD 2451544.5
    because Julian Days start at noon, not at midnight.
    """
    dt = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    jd = datetime_to_jd_ut(dt)

    assert jd == pytest.approx(2451544.5, abs=1e-9)


# ==========================================================
# jd_ut_to_datetime
# ==========================================================

def test_jd_ut_to_datetime_known_reference_j2000():
    """
    Reverse conversion of the standard J2000.0 reference.

    JD 2451545.0 -> 2000-01-01 12:00:00 UTC
    """
    dt = jd_ut_to_datetime(2451545.0)

    expected = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    assert dt == expected


def test_jd_ut_to_datetime_known_reference_midnight():
    """
    Reverse conversion for the midnight reference.

    JD 2451544.5 -> 2000-01-01 00:00:00 UTC
    """
    dt = jd_ut_to_datetime(2451544.5)

    expected = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    assert dt == expected


# ==========================================================
# Round-trip conversion
# ==========================================================

@pytest.mark.parametrize(
    "original,tolerance",
    [
        (datetime(2026, 2, 13, 18, 45, 30, tzinfo=timezone.utc), 1e-5),
        (datetime(2026, 2, 13, 18, 45, 30, 123456, tzinfo=timezone.utc), 1e-4),
    ],
)
def test_datetime_jd_round_trip(original, tolerance):
    """
    datetime -> JD -> datetime should preserve the instant
    within a very small tolerance.
    """

    jd = datetime_to_jd_ut(original)
    recovered = jd_ut_to_datetime(jd)

    delta_seconds = abs((recovered - original).total_seconds())

    assert delta_seconds < tolerance


# ==========================================================
# calc_ecl_lon_ut
# ==========================================================

def test_calc_ecl_lon_ut_returns_longitude_and_speed_for_saturn():
    """
    Basic adapter contract test.

    For a valid Julian Day and body, calc_ecl_lon_ut should return:
    - longitude as float
    - speed as float

    Longitude should be inside the zodiac range [0, 360).
    We do not assert an exact Saturn longitude yet in this file.
    """
    jd = 2451545.0  # J2000.0
    lon, speed = calc_ecl_lon_ut(jd, Body.SATURN, mode="swieph")

    assert isinstance(lon, float)
    assert isinstance(speed, float)
    assert 0.0 <= lon < 360.0


def test_calc_ecl_lon_ut_supports_moseph_mode():
    """
    The adapter exposes both:
    - 'swieph'
    - 'moseph'

    This test verifies that MOSEPH mode also returns the expected output shape.
    """
    jd = 2451545.0
    lon, speed = calc_ecl_lon_ut(jd, Body.SATURN, mode="moseph")

    assert isinstance(lon, float)
    assert isinstance(speed, float)
    assert 0.0 <= lon < 360.0


def test_calc_ecl_lon_ut_matches_direct_swiss_ephemeris_call():
    """
    Strong adapter test.

    The adapter should return the same longitude and speed
    as a direct Swiss Ephemeris call using the same flags.
    """
    jd = 2451545.0

    adapter_lon, adapter_speed = calc_ecl_lon_ut(jd, Body.SATURN, mode="swieph")

    xx, _retflag = swe.calc_ut(jd, swe.SATURN, swe.FLG_SPEED | swe.FLG_SWIEPH)
    direct_lon = float(xx[0])
    direct_speed = float(xx[3])

    assert adapter_lon == pytest.approx(direct_lon, abs=1e-12)
    assert adapter_speed == pytest.approx(direct_speed, abs=1e-12)