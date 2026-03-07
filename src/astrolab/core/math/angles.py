# src/astrolab/core/math/angles.py
from __future__ import annotations

from dataclasses import dataclass


def norm360(deg: float) -> float:
    """Normalize degrees to [0, 360)."""
    x = deg % 360.0
    return x if x >= 0 else x + 360.0


def shortest_signed_delta_deg(from_deg: float, to_deg: float) -> float:
    """
    Signed shortest angular delta from 'from_deg' to 'to_deg', in degrees, in (-180, 180].
    Example: from=359 to=1 => +2
             from=1 to=359 => -2
    """
    a = norm360(from_deg)
    b = norm360(to_deg)
    d = (b - a) % 360.0
    if d > 180.0:
        d -= 360.0
    return d


def signed_distance_to_zero(lon_deg: float) -> float:
    """
    A continuous-ish signed distance (in degrees) to 0° Aries (i.e., 0° longitude),
    using shortest path on circle.
    """
    return shortest_signed_delta_deg(lon_deg, 0.0)


@dataclass(frozen=True)
class RootResult:
    x: float
    fx: float
    iterations: int