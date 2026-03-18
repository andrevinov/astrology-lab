from datetime import datetime, timezone

import pytest
import swisseph as swe  # type: ignore

from src.astrolab.domain.bodies import Body
from src.astrolab.ephemeris.swe_adapter import (
    calc_body_positions_for_datetime,
    calc_body_positions_ut,
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
    """
    set_ephe_path(None)


# ==========================================================
# datetime_to_jd_ut
# ==========================================================

def test_datetime_to_jd_ut_rejects_non_utc_datetime():
    """
    datetime_to_jd_ut should reject datetimes that are not explicitly UTC.
    """
    dt = datetime(2026, 2, 1, 12, 0, 0)

    with pytest.raises(ValueError, match="UTC datetime"):
        datetime_to_jd_ut(dt)


def test_datetime_to_jd_ut_known_reference_j2000():
    """
    2000-01-01 12:00:00 UTC -> JD 2451545.0
    """
    dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    jd = datetime_to_jd_ut(dt)

    assert jd == pytest.approx(2451545.0, abs=1e-9)


def test_datetime_to_jd_ut_known_reference_midnight():
    """
    2000-01-01 00:00:00 UTC -> JD 2451544.5
    """
    dt = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    jd = datetime_to_jd_ut(dt)

    assert jd == pytest.approx(2451544.5, abs=1e-9)


# ==========================================================
# jd_ut_to_datetime
# ==========================================================

def test_jd_ut_to_datetime_known_reference_j2000():
    """
    JD 2451545.0 -> 2000-01-01 12:00:00 UTC
    """
    dt = jd_ut_to_datetime(2451545.0)

    expected = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    assert dt == expected


def test_jd_ut_to_datetime_known_reference_midnight():
    """
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
    For a valid Julian Day and body, calc_ecl_lon_ut should return:
    - longitude as float
    - speed as float
    """
    jd = 2451545.0
    lon, speed = calc_ecl_lon_ut(jd, Body.SATURN, mode="swieph")

    assert isinstance(lon, float)
    assert isinstance(speed, float)
    assert 0.0 <= lon < 360.0


def test_calc_ecl_lon_ut_supports_moseph_mode():
    """
    MOSEPH mode should also return the expected output shape.
    """
    jd = 2451545.0
    lon, speed = calc_ecl_lon_ut(jd, Body.SATURN, mode="moseph")

    assert isinstance(lon, float)
    assert isinstance(speed, float)
    assert 0.0 <= lon < 360.0


def test_calc_ecl_lon_ut_matches_direct_swiss_ephemeris_call():
    """
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


# ==========================================================
# calc_body_positions_ut
# ==========================================================

def test_calc_body_positions_ut_returns_multiple_bodies():
    """
    The adapter should return raw positions for multiple bodies at one JD.
    """
    jd = 2451545.0
    bodies = [Body.SATURN, Body.NEPTUNE, Body.JUPITER]

    positions = calc_body_positions_ut(jd, bodies, mode="swieph")

    assert set(positions.keys()) == {Body.SATURN, Body.NEPTUNE, Body.JUPITER}

    for body in bodies:
        lon, speed = positions[body]
        assert isinstance(lon, float)
        assert isinstance(speed, float)
        assert 0.0 <= lon < 360.0


def test_calc_body_positions_ut_matches_single_body_calls():
    """
    The multi-body helper should be consistent with repeated single-body calls.
    """
    jd = 2451545.0
    bodies = [Body.SATURN, Body.NEPTUNE]

    positions = calc_body_positions_ut(jd, bodies, mode="swieph")

    saturn_lon, saturn_speed = calc_ecl_lon_ut(jd, Body.SATURN, mode="swieph")
    neptune_lon, neptune_speed = calc_ecl_lon_ut(jd, Body.NEPTUNE, mode="swieph")

    assert positions[Body.SATURN][0] == pytest.approx(saturn_lon, abs=1e-12)
    assert positions[Body.SATURN][1] == pytest.approx(saturn_speed, abs=1e-12)
    assert positions[Body.NEPTUNE][0] == pytest.approx(neptune_lon, abs=1e-12)
    assert positions[Body.NEPTUNE][1] == pytest.approx(neptune_speed, abs=1e-12)


# ==========================================================
# calc_body_positions_for_datetime
# ==========================================================

def test_calc_body_positions_for_datetime_matches_jd_version():
    """
    The datetime-based helper should match the JD-based helper.
    """
    dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    bodies = [Body.SATURN, Body.NEPTUNE]

    by_datetime = calc_body_positions_for_datetime(dt, bodies, mode="swieph")

    jd = datetime_to_jd_ut(dt)
    by_jd = calc_body_positions_ut(jd, bodies, mode="swieph")

    assert by_datetime.keys() == by_jd.keys()

    for body in bodies:
        assert by_datetime[body][0] == pytest.approx(by_jd[body][0], abs=1e-12)
        assert by_datetime[body][1] == pytest.approx(by_jd[body][1], abs=1e-12)