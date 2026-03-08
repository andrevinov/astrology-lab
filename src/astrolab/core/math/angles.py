from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RootResult:
    """
    Generic result for numerical root-finding routines.
    """

    x: float
    fx: float
    iterations: int


def norm360(angle: float) -> float:
    """
    Normalize any angle to the half-open interval [0, 360).
    """
    return angle % 360.0


def shortest_signed_delta_deg(from_angle: float, to_angle: float) -> float:
    """
    Return the shortest signed angular difference from `from_angle` to `to_angle`,
    in degrees, in the interval [-180, 180).

    Examples:
    - from 359 to 1   -> +2
    - from 1 to 359   -> -2
    - from 10 to 190  -> -180
    """
    a = norm360(from_angle)
    b = norm360(to_angle)
    return (b - a + 180.0) % 360.0 - 180.0


def angular_distance_deg(angle_a: float, angle_b: float) -> float:
    """
    Return the absolute shortest angular distance between two angles, in [0, 180].

    Examples:
    - 359 and 1 -> 2
    - 10 and 190 -> 180
    """
    return abs(shortest_signed_delta_deg(angle_a, angle_b))


def is_within_orb(angle_a: float, angle_b: float, orb_deg: float) -> bool:
    """
    Return True if the angular distance between two angles is less than or equal to `orb_deg`.
    """
    if orb_deg < 0.0:
        raise ValueError("orb_deg must be >= 0.")
    return angular_distance_deg(angle_a, angle_b) <= orb_deg


def signed_distance_to_exact_angle(angle: float, target_angle: float) -> float:
    """
    Return the shortest signed angular distance from `angle` to `target_angle`.

    This is useful for root-finding around exact aspects or exact zodiac points.

    Examples:
    - angle=359, target=0 -> +1
    - angle=1,   target=0 -> -1
    """
    return shortest_signed_delta_deg(angle, target_angle)


def signed_distance_to_zero(angle: float) -> float:
    """
    Convenience wrapper for distance to 0°.
    """
    return signed_distance_to_exact_angle(angle, 0.0)


def all_pairwise_within_orb(angles: list[float], orb_deg: float) -> bool:
    """
    Return True if every pair of angles is within the given orb.

    This is a strict clustering criterion and works well for conjunction-like grouping.

    For example, for three angles A, B, C:
    - A must be close to B
    - A must be close to C
    - B must be close to C
    """
    if orb_deg < 0.0:
        raise ValueError("orb_deg must be >= 0.")

    n = len(angles)
    if n < 2:
        raise ValueError("angles must contain at least 2 values.")

    for i in range(n):
        for j in range(i + 1, n):
            if not is_within_orb(angles[i], angles[j], orb_deg):
                return False
    return True


def circular_span_deg(angles: list[float]) -> float:
    """
    Return the minimal circular span that contains all angles.

    This is useful for looser multi-body grouping rules, such as:
    'all bodies fit inside a window of N degrees'.

    Examples:
    - [359, 0, 1] -> 2
    - [10, 20, 30] -> 20
    - [350, 10] -> 20
    """
    if not angles:
        raise ValueError("angles must not be empty.")

    normalized = sorted(norm360(angle) for angle in angles)

    if len(normalized) == 1:
        return 0.0

    gaps: list[float] = []
    for i in range(len(normalized) - 1):
        gaps.append(normalized[i + 1] - normalized[i])

    wrap_gap = (normalized[0] + 360.0) - normalized[-1]
    gaps.append(wrap_gap)

    largest_gap = max(gaps)
    return 360.0 - largest_gap


def fits_within_circular_window(angles: list[float], window_deg: float) -> bool:
    """
    Return True if all angles fit inside a minimal circular window of size `window_deg`.

    This is an alternative clustering criterion for 3+ bodies.
    """
    if window_deg < 0.0:
        raise ValueError("window_deg must be >= 0.")
    return circular_span_deg(angles) <= window_deg