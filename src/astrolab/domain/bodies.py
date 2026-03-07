# src/astrolab/domain/bodies.py

"""
Domain definitions for astrological bodies supported by the system.

This module belongs to the domain layer. It defines the canonical
identities of celestial bodies used throughout the system.

Important:
- This module does NOT depend on Swiss Ephemeris or any external library.
- It only defines the bodies as domain concepts.
- Mapping to ephemeris identifiers is handled in the ephemeris layer.
"""

from enum import Enum


class Body(Enum):
    """Canonical astrological bodies supported by the system."""

    SUN = "sun"
    MOON = "moon"
    MERCURY = "mercury"
    VENUS = "venus"
    MARS = "mars"
    JUPITER = "jupiter"
    SATURN = "saturn"
    URANUS = "uranus"
    NEPTUNE = "neptune"
    PLUTO = "pluto"