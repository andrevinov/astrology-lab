# src/astrolab/domain/positions.py

from __future__ import annotations

from dataclasses import dataclass

from astrolab.core.math.angles import norm360
from astrolab.domain.bodies import Body


@dataclass(frozen=True)
class Position:
    """
    Position of a body at a specific instant.

    This is a domain entity that represents the essential astronomical
    state needed by the rest of the system.
    """

    body: Body
    longitude: float
    speed: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "longitude", norm360(self.longitude))
        object.__setattr__(self, "speed", float(self.speed))