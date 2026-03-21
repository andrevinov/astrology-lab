from dataclasses import dataclass

from astrolab.core.math.angles import norm360, shortest_signed_delta_deg
from astrolab.domain.bodies import Body


@dataclass(frozen=True, slots=True)
class Midpoint:
    first: Body
    second: Body
    longitude: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "longitude", norm360(self.longitude))


def midpoint_longitude(first_longitude: float, second_longitude: float) -> float:
    first = norm360(first_longitude)
    second = norm360(second_longitude)

    half_delta = shortest_signed_delta_deg(first, second) / 2.0
    return norm360(first + half_delta)


def build_midpoint(
    *,
    first: Body,
    second: Body,
    first_longitude: float,
    second_longitude: float,
) -> Midpoint:
    return Midpoint(
        first=first,
        second=second,
        longitude=midpoint_longitude(first_longitude, second_longitude),
    )