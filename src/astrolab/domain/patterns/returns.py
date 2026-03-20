from __future__ import annotations

from dataclasses import dataclass

from astrolab.core.math.angles import shortest_signed_delta_deg
from astrolab.domain.bodies import Body
from astrolab.domain.snapshots import Snapshot


@dataclass(frozen=True, slots=True)
class ReturnEvent:
    body: Body
    separation_deg: float
    orb_deg: float


def detect_return(
    natal_snapshot: Snapshot,
    transit_snapshot: Snapshot,
    *,
    body: Body,
    orb_deg: float,
) -> ReturnEvent | None:
    natal_position = natal_snapshot.position_of(body)
    transit_position = transit_snapshot.position_of(body)

    separation_deg = shortest_signed_delta_deg(
        natal_position.longitude,
        transit_position.longitude,
    )
    real_orb_deg = abs(separation_deg)

    if real_orb_deg > orb_deg:
        return None

    return ReturnEvent(
        body=body,
        separation_deg=separation_deg,
        orb_deg=real_orb_deg,
    )