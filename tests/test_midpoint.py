import math

from src.astrolab.domain.bodies import Body
from src.astrolab.domain.patterns.midpoints import (
    build_midpoint,
    midpoint_longitude,
)


def almost_equal(a: float, b: float, tol: float = 1e-9) -> bool:
    return math.isclose(a, b, abs_tol=tol)


def test_midpoint_simple_case():
    # 10° and 20° -> 15°
    result = midpoint_longitude(10.0, 20.0)
    assert almost_equal(result, 15.0)


def test_midpoint_wrap_around():
    # 350° and 10° -> 0°
    result = midpoint_longitude(350.0, 10.0)
    assert almost_equal(result, 0.0)

def test_midpoint_normalization_of_inputs():
    # 370° -> 10°, -10° -> 350°, midpoint = 0°
    result = midpoint_longitude(370.0, -10.0)
    assert almost_equal(result, 0.0)

def test_midpoint_opposition_convention():
    # 0° and 180° -> by convention (using shortest_signed_delta_deg),
    # midpoint should be 270° (not 90°)
    result = midpoint_longitude(0.0, 180.0)
    assert almost_equal(result, 270.0)


def test_build_midpoint_structure():
    midpoint = build_midpoint(
        first=Body.SUN,
        second=Body.MOON,
        first_longitude=10.0,
        second_longitude=20.0,
    )

    assert midpoint.first == Body.SUN
    assert midpoint.second == Body.MOON
    assert almost_equal(midpoint.longitude, 15.0)


def test_midpoint_longitude_is_normalized_in_dataclass():
    midpoint = build_midpoint(
        first=Body.MARS,
        second=Body.VENUS,
        first_longitude=350.0,
        second_longitude=10.0,
    )

    # midpoint should be 0°, and guaranteed normalized
    assert 0.0 <= midpoint.longitude < 360.0
    assert almost_equal(midpoint.longitude, 0.0)