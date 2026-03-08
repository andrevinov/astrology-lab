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


@dataclass(frozen=True)
class SearchWindow:
    """
    Generic UTC time window used by scanners and event search use cases.
    """
    start_utc: datetime
    end_utc: datetime

    def __post_init__(self) -> None:
        if self.start_utc.tzinfo is None or self.end_utc.tzinfo is None:
            raise ValueError("SearchWindow requires aware datetimes.")
        if self.start_utc.tzinfo != timezone.utc or self.end_utc.tzinfo != timezone.utc:
            raise ValueError("SearchWindow requires timezone.utc datetimes.")
        if not (self.start_utc < self.end_utc):
            raise ValueError("SearchWindow requires start_utc < end_utc.")


def ensure_utc(dt: datetime) -> UTCDateTime:
    """
    Normalize an aware datetime to timezone.utc and wrap it explicitly.
    """
    if dt.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware.")
    return UTCDateTime(dt.astimezone(timezone.utc))