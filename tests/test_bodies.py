# tests/test_bodies.py

from astrolab.domain.bodies import Body


def test_body_enum_contains_expected_members():
    """Ensure the Body enum contains the canonical set of supported bodies."""
    expected = {
        Body.SUN,
        Body.MOON,
        Body.MERCURY,
        Body.VENUS,
        Body.MARS,
        Body.JUPITER,
        Body.SATURN,
        Body.URANUS,
        Body.NEPTUNE,
        Body.PLUTO,
    }

    assert set(Body) == expected


def test_body_values_are_stable_strings():
    """Ensure the enum values are stable canonical identifiers."""
    assert Body.SUN.value == "sun"
    assert Body.MOON.value == "moon"
    assert Body.SATURN.value == "saturn"
    assert Body.NEPTUNE.value == "neptune"


def test_body_lookup_by_name():
    """Ensure enum lookup by name works."""
    assert Body["SATURN"] is Body.SATURN
    assert Body["NEPTUNE"] is Body.NEPTUNE


def test_body_lookup_by_value():
    """Ensure enum lookup by value works."""
    assert Body("saturn") is Body.SATURN
    assert Body("neptune") is Body.NEPTUNE