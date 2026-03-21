# tests/test_swe_adapter.py
#
# Unit tests for the Swiss Ephemeris adapter.
#
# This module validates that our adapter layer correctly:
#
# 1. Converts time between UTC datetime and Julian Day (UT)
# 2. Enforces explicit UTC datetimes
# 3. Returns correct planetary longitude and speed values
#    consistent with direct Swiss Ephemeris calls.

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, Literal, Tuple

import swisseph as swe  # type: ignore

from astrolab.domain.bodies import Body

EPHE_MODE = Literal["swieph", "moseph"]
RawBodyPosition = Tuple[float, float]
RawBodyPositionMap = Dict[Body, RawBodyPosition]


BODY_TO_SWE = {
    Body.SUN: swe.SUN,
    Body.MOON: swe.MOON,
    Body.MERCURY: swe.MERCURY,
    Body.VENUS: swe.VENUS,
    Body.MARS: swe.MARS,
    Body.JUPITER: swe.JUPITER,
    Body.SATURN: swe.SATURN,
    Body.URANUS: swe.URANUS,
    Body.NEPTUNE: swe.NEPTUNE,
    Body.PLUTO: swe.PLUTO,
}


def set_ephe_path(path: str | None = None) -> None:
    """
    Configure where Swiss Ephemeris looks for ephemeris files.
    If you don't have .se1 files, calculations may still work with MOSEPH mode.
    """
    swe.set_ephe_path("" if path is None else path)


def datetime_to_jd_ut(dt_utc: datetime) -> float:
    """
    Convert a timezone.utc datetime into Julian Day (UT).
    """
    if dt_utc.tzinfo != timezone.utc:
        raise ValueError("datetime_to_jd_ut expects a UTC datetime (timezone.utc).")

    y, m, d = dt_utc.year, dt_utc.month, dt_utc.day
    hour = (
        dt_utc.hour
        + dt_utc.minute / 60.0
        + dt_utc.second / 3600.0
        + dt_utc.microsecond / 3_600_000_000.0
    )
    return swe.julday(y, m, d, hour, swe.GREG_CAL)


def jd_ut_to_datetime(jd_ut: float) -> datetime:
    """
    Convert Julian Day (UT) back into a timezone.utc datetime.
    """
    y, m, d, hour = swe.revjul(jd_ut, swe.GREG_CAL)

    total_microseconds = round(hour * 3_600_000_000)

    hours, remainder = divmod(total_microseconds, 3_600_000_000)
    minutes, remainder = divmod(remainder, 60_000_000)
    seconds, microseconds = divmod(remainder, 1_000_000)

    if hours >= 24:
        hours -= 24
        base = datetime(y, m, d, tzinfo=timezone.utc) + timedelta(days=1)
        return base.replace(
            hour=hours,
            minute=minutes,
            second=seconds,
            microsecond=microseconds,
        )

    return datetime(
        y,
        m,
        d,
        hours,
        minutes,
        seconds,
        microsecond=microseconds,
        tzinfo=timezone.utc,
    )


def _build_iflag(mode: EPHE_MODE) -> int:
    """
    Build the Swiss Ephemeris flag set for longitude + speed calculation.
    """
    iflag = swe.FLG_SPEED
    if mode == "swieph":
        iflag |= swe.FLG_SWIEPH
    else:
        iflag |= swe.FLG_MOSEPH
    return iflag


def calc_ecl_lon_ut(jd_ut: float, body: Body, mode: EPHE_MODE = "swieph") -> RawBodyPosition:
    """
    Return (longitude_degrees, speed_deg_per_day) for a single body at a given Julian Day (UT).

    Tropical zodiac by default (Swiss Ephemeris default).
    """
    swe_body = BODY_TO_SWE[body]
    iflag = _build_iflag(mode)

    xx, _retflag = swe.calc_ut(jd_ut, swe_body, iflag)
    lon = float(xx[0])
    speed = float(xx[3])
    return lon, speed


def calc_body_positions_ut(
    jd_ut: float,
    bodies: Iterable[Body],
    mode: EPHE_MODE = "swieph",
) -> RawBodyPositionMap:
    """
    Return raw body positions for multiple bodies at a given Julian Day (UT).

    Output shape:
        {
            Body.SATURN: (longitude_degrees, speed_deg_per_day),
            Body.NEPTUNE: (longitude_degrees, speed_deg_per_day),
            ...
        }

    This function intentionally returns raw adapter data only.
    It does not build domain entities such as Position or Snapshot.
    """
    result: RawBodyPositionMap = {}
    for body in bodies:
        result[body] = calc_ecl_lon_ut(jd_ut, body, mode=mode)
    return result


def calc_body_positions_for_datetime(
    dt_utc: datetime,
    bodies: Iterable[Body],
    mode: EPHE_MODE = "swieph",
) -> RawBodyPositionMap:
    """
    Return raw body positions for multiple bodies at a given UTC datetime.
    """
    jd_ut = datetime_to_jd_ut(dt_utc)
    return calc_body_positions_ut(jd_ut, bodies, mode=mode)