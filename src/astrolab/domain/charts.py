# src/astrolab/domain/charts.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.astrolab.domain.bodies import Body
from src.astrolab.domain.positions import Position
from src.astrolab.domain.snapshots import Snapshot


@dataclass(frozen=True)
class Chart:
    """
    A Chart is a named astrological chart built on top of a sky snapshot.

    Domain intent:
    - Snapshot stores the actual positions at a UTC instant
    - Chart adds chart-level identity and minimal metadata
    - Interpretation is not stored here; this is still a pure domain entity
    """

    snapshot: Snapshot
    name: Optional[str] = None
    chart_type: str = "generic"
    zodiac: str = "tropical"
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.snapshot, Snapshot):
            raise TypeError("Chart.snapshot must be a Snapshot instance.")

        if not self.chart_type or not self.chart_type.strip():
            raise ValueError("Chart.chart_type must be a non-empty string.")

        if not self.zodiac or not self.zodiac.strip():
            raise ValueError("Chart.zodiac must be a non-empty string.")

        object.__setattr__(self, "chart_type", self.chart_type.strip())
        object.__setattr__(self, "zodiac", self.zodiac.strip().lower())

        if self.name is not None:
            cleaned_name = self.name.strip()
            object.__setattr__(self, "name", cleaned_name or None)

        if self.notes is not None:
            cleaned_notes = self.notes.strip()
            object.__setattr__(self, "notes", cleaned_notes or None)

    @property
    def timestamp_utc(self):
        """Expose the chart timestamp directly from the underlying snapshot."""
        return self.snapshot.timestamp_utc

    @property
    def bodies(self) -> tuple[Body, ...]:
        """Return the bodies present in this chart."""
        return self.snapshot.bodies

    @property
    def positions(self) -> tuple[Position, ...]:
        """Return all positions present in this chart."""
        return self.snapshot.positions

    def has_body(self, body: Body) -> bool:
        """Return whether the chart contains the requested body."""
        return self.snapshot.has_body(body)

    def position_of(self, body: Body) -> Position:
        """Return the position for a given body."""
        return self.snapshot.position_of(body)