# src/astrolab/core/time/jd.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class UTCDateTime:
    """
    Small wrapper to make 'UTC-ness' explicit.
    """
    dt: datetime

    def __post_init__(self) -> None:
        if self.dt.tzinfo is None:
            raise ValueError("UTCDateTime requires an aware datetime with tzinfo.")
        if self.dt.tzinfo != timezone.utc:
            raise ValueError("UTCDateTime requires timezone.utc.")


def ensure_utc(dt: datetime) -> UTCDateTime:
    if dt.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware.")
    return UTCDateTime(dt.astimezone(timezone.utc))


def datetime_to_jd_ut(dt_utc: datetime) -> float:
    """
    Convert aware UTC datetime to Julian Day (UT).
    Implemented via Swiss Ephemeris in ephemeris layer; here we keep it pure/simple.
    This function is intentionally NOT implemented here to avoid importing swe in core.
    """
    raise NotImplementedError("Use ephemeris.swe_adapter.datetime_to_jd_ut()")


def jd_ut_to_datetime(jd_ut: float) -> datetime:
    """
    Convert JD(UT) -> aware UTC datetime.
    Implemented via Swiss Ephemeris in ephemeris layer; here we keep it pure/simple.
    """
    raise NotImplementedError("Use ephemeris.swe_adapter.jd_ut_to_datetime()")