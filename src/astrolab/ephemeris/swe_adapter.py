# src/astrolab/ephemeris/swe_adapter.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Literal, Tuple

import swisseph as swe  # type: ignore

EPHE_MODE = Literal["swieph", "moseph"]


def set_ephe_path(path: str | None = None) -> None:
    """
    Configure where Swiss Ephemeris looks for ephemeris files.
    If you don't have .se1 files, we'll fall back to MOSEPH flags in calculations.
    """
    swe.set_ephe_path("" if path is None else path)


def datetime_to_jd_ut(dt_utc: datetime) -> float:
    if dt_utc.tzinfo != timezone.utc:
        raise ValueError("datetime_to_jd_ut expects a UTC datetime (timezone.utc).")
    y, m, d = dt_utc.year, dt_utc.month, dt_utc.day
    hour = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0 + dt_utc.microsecond / 3_600_000_000.0
    return swe.julday(y, m, d, hour, swe.GREG_CAL)


def jd_ut_to_datetime(jd_ut: float) -> datetime:
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
        microseconds,
        tzinfo=timezone.utc,
    )


def calc_ecl_lon_ut(jd_ut: float, body: int, mode: EPHE_MODE = "swieph") -> Tuple[float, float]:
    """
    Returns (longitude_degrees, speed_deg_per_day).
    Tropical zodiac by default (Swiss Ephemeris default).
    """
    iflag = swe.FLG_SPEED
    if mode == "swieph":
        iflag |= swe.FLG_SWIEPH
    else:
        iflag |= swe.FLG_MOSEPH

    xx, retflag = swe.calc_ut(jd_ut, body, iflag)
    lon = float(xx[0])
    speed = float(xx[3])
    return lon, speed