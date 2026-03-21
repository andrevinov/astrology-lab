# tests/test_positions.py

import pytest

from astrolab.domain.bodies import Body
from astrolab.domain.positions import Position


def test_position_stores_body_longitude_and_speed():
    """Position should store the essential fields for a body at an instant."""
    position = Position(body=Body.MOON, longitude=123.45, speed=13.2)

    assert position.body is Body.MOON
    assert position.longitude == 123.45
    assert position.speed == 13.2


def test_position_normalizes_longitude_into_0_360_range():
    """Longitude should always be normalized to the canonical [0, 360) range."""
    assert Position(body=Body.SUN, longitude=361.0, speed=0.95).longitude == 1.0
    assert Position(body=Body.SUN, longitude=-1.0, speed=0.95).longitude == 359.0
    assert Position(body=Body.SUN, longitude=360.0, speed=0.95).longitude == 0.0


def test_position_converts_speed_to_float():
    """Speed should be stored as float for consistency across calculations."""
    position = Position(body=Body.MARS, longitude=10.0, speed=1)

    assert position.speed == 1.0
    assert isinstance(position.speed, float)


def test_position_is_immutable():
    """Position should be immutable once created."""
    position = Position(body=Body.VENUS, longitude=42.0, speed=1.2)

    with pytest.raises(AttributeError):
        position.longitude = 50.0