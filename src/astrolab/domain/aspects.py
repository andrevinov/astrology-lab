# src/astrolab/domain/aspects.py

from __future__ import annotations

from enum import Enum

from astrolab.core.math.angles import norm360


class Aspect(Enum):
    """
    Canonical astrological aspects supported by the system.

    The enum value is the exact angular separation associated
    with the aspect in degrees.
    """

    CONJUNCTION = 0.0
    SEXTILE = 60.0
    SQUARE = 90.0
    TRINE = 120.0
    OPPOSITION = 180.0

    @property
    def angle(self) -> float:
        """Return the exact angular separation of the aspect."""
        return float(self.value)


def angular_separation(angle_a: float, angle_b: float) -> float:
    """
    Return the minimum angular separation between two angles.

    The result is always in the closed interval [0, 180].
    """
    a = norm360(angle_a)
    b = norm360(angle_b)

    delta = abs(a - b)
    return min(delta, 360.0 - delta)


def detect_aspect(angle_a: float, angle_b: float, orb: float) -> Aspect | None:
    """
    Detect the major aspect between two angles using a global orb.

    Rules:
    - orb must be non-negative
    - the closest supported major aspect within orb is returned
    - if no aspect is within orb, return None

    Supported aspects:
    - conjunction (0°)
    - sextile (60°)
    - square (90°)
    - trine (120°)
    - opposition (180°)
    """
    if orb < 0:
        raise ValueError("orb must be non-negative")

    delta = angular_separation(angle_a, angle_b)

    best_match: Aspect | None = None
    best_distance: float | None = None

    for aspect in Aspect:
        distance = abs(delta - aspect.angle)
        if distance <= orb:
            if best_distance is None or distance < best_distance:
                best_match = aspect
                best_distance = distance

    return best_match