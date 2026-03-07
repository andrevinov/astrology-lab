# src/astrolab/domain/bodies.py
from __future__ import annotations

import swisseph as swe  # type: ignore


class Body:
    """
    Domain-level identifiers for celestial bodies we care about.
    """
    SATURN = swe.SATURN