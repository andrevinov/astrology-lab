# tests/test_aspects.py
#
# Unit tests for astrological aspect detection.
#
# This module validates that the domain layer correctly:
#
# 1. Computes the minimum angular separation between two angles
# 2. Detects major aspects using a global orb
# 3. Rejects invalid orb values
# 4. Handles zodiac wrap-around correctly

import pytest

from src.astrolab.domain.aspects import Aspect, angular_separation, detect_aspect

# ==========================================================
# angular_separation
# ==========================================================

def test_angular_separation_returns_zero_for_equal_angles():
    """
    If both angles are the same, the separation should be 0 degrees.
    """
    assert angular_separation(10.0, 10.0) == pytest.approx(0.0)


def test_angular_separation_returns_direct_distance_when_under_180():
    """
    When the direct difference is already the shortest path,
    the function should return that direct angular distance.
    """
    assert angular_separation(10.0, 70.0) == pytest.approx(60.0)


def test_angular_separation_uses_shorter_arc_when_over_180():
    """
    Angular separation must always use the smallest arc on the circle.

    Example:
    10° and 250° are 240° apart directly, but only 120° apart
    through the shorter path.
    """
    assert angular_separation(10.0, 250.0) == pytest.approx(120.0)


def test_angular_separation_handles_wrap_around_near_zero_aries():
    """
    Angles near 0° Aries should still be treated as close to each other.

    Example:
    359° and 1° are only 2° apart, not 358°.
    """
    assert angular_separation(359.0, 1.0) == pytest.approx(2.0)


def test_angular_separation_normalizes_input_angles():
    """
    Input angles may fall outside the 0-360 range.

    The function should normalize them before computing
    the minimum angular distance.
    """
    assert angular_separation(370.0, -10.0) == pytest.approx(20.0)


# ==========================================================
# detect_aspect
# ==========================================================

def test_detect_aspect_rejects_negative_orb():
    """
    A negative orb is invalid and should raise a ValueError.
    """
    with pytest.raises(ValueError, match="orb must be non-negative"):
        detect_aspect(0.0, 60.0, orb=-1.0)


@pytest.mark.parametrize(
    "angle_a,angle_b,expected",
    [
        (10.0, 10.0, Aspect.CONJUNCTION),
        (10.0, 70.0, Aspect.SEXTILE),
        (10.0, 100.0, Aspect.SQUARE),
        (10.0, 130.0, Aspect.TRINE),
        (10.0, 190.0, Aspect.OPPOSITION),
    ],
)
def test_detect_aspect_identifies_exact_major_aspects(angle_a, angle_b, expected):
    """
    Exact canonical separations should be classified as their
    corresponding major aspects when orb is zero.
    """
    assert detect_aspect(angle_a, angle_b, orb=0.0) is expected


def test_detect_aspect_detects_aspect_within_orb():
    """
    A separation slightly away from the exact aspect angle
    should still be detected when it falls within the global orb.

    Example:
    62° is within a 3° orb of the sextile at 60°.
    """
    result = detect_aspect(0.0, 62.0, orb=3.0)

    assert result is Aspect.SEXTILE


def test_detect_aspect_returns_none_when_outside_orb():
    """
    If the separation is outside the allowed orb for every
    supported aspect, the function should return None.

    Example:
    64° is outside a 3° orb from sextile.
    """
    result = detect_aspect(0.0, 64.0, orb=3.0)

    assert result is None


def test_detect_aspect_handles_wrap_around_for_conjunction():
    """
    Angles across the 0°/360° boundary should still be recognized.

    Example:
    359° and 1° are 2° apart, so they form a conjunction
    within a 2° orb.
    """
    result = detect_aspect(359.0, 1.0, orb=2.0)

    assert result is Aspect.CONJUNCTION


def test_detect_aspect_handles_wrap_around_for_opposition():
    """
    Wrap-around logic must also work for larger aspect angles.

    Example:
    359° and 179° are 180° apart by minimum separation,
    so they form an opposition.
    """
    result = detect_aspect(359.0, 179.0, orb=0.0)

    assert result is Aspect.OPPOSITION


def test_detect_aspect_returns_closest_matching_aspect_when_multiple_fit():
    """
    With a large orb, more than one aspect may technically fit.

    In this case, the function should return the closest aspect
    by exact angular distance.

    Example:
    75° is:
    - 15° from sextile (60°)
    - 15° from square (90°)

    This test documents the current tie behavior produced by
    enum iteration order: the first equally-close aspect wins.
    """
    result = detect_aspect(0.0, 75.0, orb=15.0)

    assert result is Aspect.SEXTILE


def test_detect_aspect_normalizes_input_angles_before_detection():
    """
    Aspect detection should work even if the provided angles
    are outside the canonical 0-360 range.
    """
    result = detect_aspect(370.0, 430.0, orb=0.0)

    assert result is Aspect.SEXTILE


def test_detect_aspect_detects_square_just_inside_orb():
    """
    A value just inside the orb boundary should still count.

    Example:
    92° is within a 2° orb of square.
    """
    result = detect_aspect(0.0, 92.0, orb=2.0)

    assert result is Aspect.SQUARE


def test_detect_aspect_rejects_square_just_outside_orb():
    """
    A value just beyond the orb boundary should not count.

    Example:
    92.01° is outside a 2° orb of square.
    """
    result = detect_aspect(0.0, 92.01, orb=2.0)

    assert result is None