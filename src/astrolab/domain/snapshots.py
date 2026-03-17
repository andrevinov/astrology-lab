from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping

from src.astrolab.core.time.jd import UTCDateTime
from src.astrolab.domain.bodies import Body
from src.astrolab.domain.positions import Position


@dataclass(frozen=True)
class Snapshot:
    """
    Snapshot = a "photo of the sky" at a specific UTC instant.

    Domain rule:
    - timestamp_utc must already be an explicit UTCDateTime
    - positions_by_body stores exactly one Position per Body
    """

    timestamp_utc: UTCDateTime
    positions_by_body: Mapping[Body, Position]

    def __post_init__(self) -> None:
        if not isinstance(self.timestamp_utc, UTCDateTime):
            raise TypeError("Snapshot.timestamp_utc must be a UTCDateTime instance.")

        pb = dict(self.positions_by_body)
        if not pb:
            raise ValueError("Snapshot must contain at least one Position.")

        for body, pos in pb.items():
            if pos.body != body:
                raise ValueError(
                    f"Inconsistent position map: key body={body} but pos.body={pos.body}"
                )

        object.__setattr__(self, "positions_by_body", pb)

    @property
    def bodies(self) -> tuple[Body, ...]:
        return tuple(self.positions_by_body.keys())

    @property
    def positions(self) -> tuple[Position, ...]:
        return tuple(self.positions_by_body.values())

    def has_body(self, body: Body) -> bool:
        return body in self.positions_by_body

    def position_of(self, body: Body) -> Position:
        try:
            return self.positions_by_body[body]
        except KeyError as e:
            raise KeyError(f"Body not present in snapshot: {body}") from e

    @classmethod
    def from_positions(
        cls,
        timestamp_utc: UTCDateTime,
        positions: Iterable[Position],
    ) -> "Snapshot":
        if not isinstance(timestamp_utc, UTCDateTime):
            raise TypeError("Snapshot.from_positions requires timestamp_utc as UTCDateTime.")

        positions_list = list(positions)
        if not positions_list:
            raise ValueError("Snapshot requires at least one Position.")

        pb: Dict[Body, Position] = {}
        for position in positions_list:
            if position.body in pb:
                raise ValueError(
                    f"Duplicate body in snapshot positions: {position.body}"
                )
            pb[position.body] = position

        return cls(timestamp_utc=timestamp_utc, positions_by_body=pb)