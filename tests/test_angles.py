# tests/test_angles.py
#
# Unit tests for src/astrolab/core/math/angles.py
#
# Why are these tests important?
# Astrology calculations operate on a circular system (0° == 360°).
# If circular arithmetic fails here, every higher-level concept
# (conjunctions, oppositions, quadratures, ingresses, orbs, clustering)
# will be wrong.
#
# These tests validate:
# - Angle normalization
# - Circular shortest angular distance
# - Sign conventions
# - Absolute angular distance
# - Orb checks
# - Circular clustering / span behavior
# - Edge cases (0°, 180°, wrap-around)
# - Immutability of result structures

import pytest

from src.astrolab.core.math.angles import (
    RootResult,
    all_pairwise_within_orb,
    angular_distance_deg,
    circular_span_deg,
    fits_within_circular_window,
    is_within_orb,
    norm360,
    shortest_signed_delta_deg,
    signed_distance_to_exact_angle,
    signed_distance_to_zero,
)


# ==========================================================
# norm360
# ==========================================================

def test_norm360_preserves_valid_range():
    """
    norm360 should:
    - Keep 0 as 0
    - Convert 360 to 0 (since 360° == 0° on a circle)
    - Leave values already in [0, 360) unchanged
    """
    assert norm360(0.0) == 0.0
    assert norm360(360.0) == 0.0
    assert norm360(15.25) == 15.25
    assert norm360(359.999) == 359.999


def test_norm360_wraps_negative_values():
    """
    Negative angles should wrap correctly into [0, 360).

    Example:
    -1° == 359°
    """
    assert norm360(-1.0) == 359.0
    assert norm360(-360.0) == 0.0
    assert norm360(-361.0) == 359.0


def test_norm360_wraps_large_values():
    """
    Values above 360 must wrap correctly.

    Example:
    361° == 1°
    """
    assert norm360(361.0) == 1.0
    assert norm360(720.0) == 0.0
    assert norm360(725.0) == 5.0


# ==========================================================
# shortest_signed_delta_deg
# ==========================================================

def test_shortest_signed_delta_same_angle_is_zero():
    """
    If both angles represent the same point,
    the delta must be zero.
    """
    assert shortest_signed_delta_deg(0.0, 0.0) == 0.0
    assert shortest_signed_delta_deg(123.456, 123.456) == 0.0
    assert shortest_signed_delta_deg(360.0, 0.0) == 0.0


def test_shortest_signed_delta_simple_forward_backward():
    """
    Without wrap-around:

    10° -> 20° = +10
    20° -> 10° = -10
    """
    assert shortest_signed_delta_deg(10.0, 20.0) == 10.0
    assert shortest_signed_delta_deg(20.0, 10.0) == -10.0


def test_shortest_signed_delta_wraparound_across_zero():
    """
    Classic zodiac boundary case:

    359° -> 1° = +2° (move forward 2 degrees)
    1° -> 359° = -2° (move backward 2 degrees)
    """
    assert shortest_signed_delta_deg(359.0, 1.0) == 2.0
    assert shortest_signed_delta_deg(1.0, 359.0) == -2.0


def test_shortest_signed_delta_returns_in_minus180_to_180_interval():
    """
    The function guarantees results in [-180, 180).

    180° is a degenerate case:
    both +180 and -180 are valid minimal distances.
    By convention, this implementation returns -180.
    """
    assert shortest_signed_delta_deg(0.0, 180.0) == -180.0
    assert shortest_signed_delta_deg(180.0, 0.0) == -180.0


def test_shortest_signed_delta_antisymmetry_property():
    """
    Mathematical property:

    delta(a -> b) should be approximately
    the negative of delta(b -> a),
    except in the degenerate 180° case.
    """
    a, b = 10.0, 200.0
    dab = shortest_signed_delta_deg(a, b)
    dba = shortest_signed_delta_deg(b, a)

    assert pytest.approx(dab, abs=1e-12) == -dba

    # Degenerate case (180°)
    a2, b2 = 0.0, 180.0
    assert shortest_signed_delta_deg(a2, b2) == -180.0
    assert shortest_signed_delta_deg(b2, a2) == -180.0


# ==========================================================
# angular_distance_deg
# ==========================================================

def test_angular_distance_deg_basic_and_wraparound_cases():
    """
    angular_distance_deg returns the absolute shortest distance
    between two angles on the circle.
    """
    assert angular_distance_deg(10.0, 20.0) == 10.0
    assert angular_distance_deg(20.0, 10.0) == 10.0
    assert angular_distance_deg(359.0, 1.0) == 2.0
    assert angular_distance_deg(1.0, 359.0) == 2.0
    assert angular_distance_deg(0.0, 180.0) == 180.0


# ==========================================================
# is_within_orb
# ==========================================================

def test_is_within_orb_basic_and_wraparound_cases():
    """
    is_within_orb should work both in regular and wrap-around scenarios.
    """
    assert is_within_orb(10.0, 12.0, 2.0) is True
    assert is_within_orb(10.0, 13.0, 2.0) is False
    assert is_within_orb(359.0, 1.0, 2.0) is True
    assert is_within_orb(359.0, 1.0, 1.5) is False


def test_is_within_orb_rejects_negative_orb():
    """
    Orb must be non-negative.
    """
    with pytest.raises(ValueError, match="orb_deg must be >= 0."):
        is_within_orb(10.0, 12.0, -1.0)


# ==========================================================
# signed_distance_to_exact_angle
# ==========================================================

def test_signed_distance_to_exact_angle_basic_examples():
    """
    signed_distance_to_exact_angle(x, target) measures
    the shortest signed angular distance to the target angle.
    """
    assert signed_distance_to_exact_angle(359.0, 0.0) == 1.0
    assert signed_distance_to_exact_angle(1.0, 0.0) == -1.0
    assert signed_distance_to_exact_angle(10.0, 20.0) == 10.0
    assert signed_distance_to_exact_angle(20.0, 10.0) == -10.0


# ==========================================================
# signed_distance_to_zero
# ==========================================================

def test_signed_distance_to_zero_basic_neighbors():
    """
    signed_distance_to_zero(x) measures
    the shortest signed angular distance to 0°.

    Consequences:
    - 0° -> 0
    - 359° -> +1 (move forward 1° to reach 0)
    - 1° -> -1 (move backward 1° to reach 0)
    """
    assert signed_distance_to_zero(0.0) == 0.0
    assert signed_distance_to_zero(359.0) == 1.0
    assert signed_distance_to_zero(1.0) == -1.0


def test_signed_distance_to_zero_quadrant_examples():
    """
    Useful mental visualization:

    - 90° is -90° away from 0 (go backward)
    - 270° is +90° away from 0 (go forward)
    """
    assert signed_distance_to_zero(90.0) == -90.0
    assert signed_distance_to_zero(270.0) == 90.0


def test_signed_distance_to_zero_180_degrees():
    """
    180° is the degenerate midpoint on the circle.
    By convention, we expect -180.
    """
    assert signed_distance_to_zero(180.0) == -180.0


# ==========================================================
# all_pairwise_within_orb
# ==========================================================

def test_all_pairwise_within_orb_for_two_and_three_angles():
    """
    all_pairwise_within_orb should require every pair
    in the set to satisfy the orb constraint.
    """
    assert all_pairwise_within_orb([10.0, 11.5], 2.0) is True
    assert all_pairwise_within_orb([359.0, 0.5, 1.0], 2.0) is True
    assert all_pairwise_within_orb([359.0, 1.0, 4.5], 2.0) is False


def test_all_pairwise_within_orb_rejects_invalid_inputs():
    """
    The function requires at least two angles and a non-negative orb.
    """
    with pytest.raises(ValueError, match="angles must contain at least 2 values."):
        all_pairwise_within_orb([10.0], 2.0)

    with pytest.raises(ValueError, match="orb_deg must be >= 0."):
        all_pairwise_within_orb([10.0, 12.0], -1.0)


# ==========================================================
# circular_span_deg
# ==========================================================

def test_circular_span_deg_basic_and_wraparound_clusters():
    """
    circular_span_deg returns the minimal circular span
    that contains all given angles.
    """
    assert circular_span_deg([42.0]) == 0.0
    assert circular_span_deg([10.0, 20.0, 30.0]) == 20.0
    assert circular_span_deg([359.0, 0.0, 1.0]) == 2.0
    assert circular_span_deg([350.0, 10.0]) == 20.0


def test_circular_span_deg_rejects_empty_input():
    """
    The function requires at least one angle.
    """
    with pytest.raises(ValueError, match="angles must not be empty."):
        circular_span_deg([])


# ==========================================================
# fits_within_circular_window
# ==========================================================

def test_fits_within_circular_window_basic_examples():
    """
    fits_within_circular_window should return True when all angles
    fit inside a minimal circular span smaller than or equal to the window.
    """
    assert fits_within_circular_window([359.0, 0.0, 1.0], 2.0) is True
    assert fits_within_circular_window([359.0, 0.0, 1.0], 1.5) is False
    assert fits_within_circular_window([10.0, 20.0, 30.0], 20.0) is True
    assert fits_within_circular_window([10.0, 20.0, 30.0], 19.9) is False


def test_fits_within_circular_window_rejects_negative_window():
    """
    Window size must be non-negative.
    """
    with pytest.raises(ValueError, match="window_deg must be >= 0."):
        fits_within_circular_window([10.0, 20.0], -1.0)


# ==========================================================
# RootResult (design sanity check)
# ==========================================================

def test_rootresult_is_immutable():
    """
    RootResult is defined as a frozen dataclass.

    This guarantees that once a root-finding result
    is created, it cannot be mutated.
    """
    r = RootResult(x=1.0, fx=0.1, iterations=3)

    with pytest.raises(Exception):
        r.x = 2.0  # type: ignore