from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.astrolab.core.time.jd import UTCDateTime
from src.astrolab.domain.bodies import Body
from src.astrolab.domain.positions import Position
from src.astrolab.domain.snapshots import Snapshot


def test_snapshot_from_positions_builds_mapping_and_allows_lookup() -> None:
    ts = UTCDateTime(datetime(2026, 2, 20, 16, 13, tzinfo=timezone.utc))

    p_saturn = Position(body=Body.SATURN, longitude=0.01, speed=0.0)
    p_neptune = Position(body=Body.NEPTUNE, longitude=0.00, speed=0.0)

    snap = Snapshot.from_positions(timestamp_utc=ts, positions=[p_saturn, p_neptune])

    assert snap.timestamp_utc == ts

    assert snap.has_body(Body.SATURN) is True
    assert snap.has_body(Body.NEPTUNE) is True
    assert snap.has_body(Body.SUN) is False

    assert snap.position_of(Body.SATURN) == p_saturn
    assert snap.position_of(Body.NEPTUNE) == p_neptune


def test_snapshot_bodies_and_positions_properties_are_consistent() -> None:
    ts = UTCDateTime(datetime(2026, 2, 20, 16, 13, tzinfo=timezone.utc))

    p_saturn = Position(body=Body.SATURN, longitude=0.01, speed=0.0)
    p_neptune = Position(body=Body.NEPTUNE, longitude=0.00, speed=0.0)

    snap = Snapshot.from_positions(timestamp_utc=ts, positions=[p_saturn, p_neptune])

    assert snap.bodies == (Body.SATURN, Body.NEPTUNE)
    assert snap.positions == (p_saturn, p_neptune)


def test_snapshot_requires_at_least_one_position_in_constructor() -> None:
    ts = UTCDateTime(datetime(2026, 2, 20, 16, 13, tzinfo=timezone.utc))

    with pytest.raises(ValueError, match="at least one Position"):
        Snapshot(timestamp_utc=ts, positions_by_body={})


def test_snapshot_requires_at_least_one_position_in_from_positions() -> None:
    ts = UTCDateTime(datetime(2026, 2, 20, 16, 13, tzinfo=timezone.utc))

    with pytest.raises(ValueError, match="at least one Position"):
        Snapshot.from_positions(timestamp_utc=ts, positions=[])


def test_snapshot_rejects_duplicate_bodies_in_from_positions() -> None:
    ts = UTCDateTime(datetime(2026, 2, 20, 16, 13, tzinfo=timezone.utc))

    p1 = Position(body=Body.SATURN, longitude=0.01, speed=0.0)
    p2 = Position(body=Body.SATURN, longitude=0.02, speed=0.0)

    with pytest.raises(ValueError, match="Duplicate body"):
        Snapshot.from_positions(timestamp_utc=ts, positions=[p1, p2])


def test_snapshot_rejects_non_utcdatetime_timestamp_in_constructor() -> None:
    ts = datetime(2026, 2, 20, 16, 13, tzinfo=timezone.utc)
    p_saturn = Position(body=Body.SATURN, longitude=0.01, speed=0.0)

    with pytest.raises(TypeError, match="must be a UTCDateTime"):
        Snapshot(timestamp_utc=ts, positions_by_body={Body.SATURN: p_saturn}) # type: ignore


def test_snapshot_rejects_non_utcdatetime_timestamp_in_from_positions() -> None:
    ts = datetime(2026, 2, 20, 16, 13, tzinfo=timezone.utc)
    p_saturn = Position(body=Body.SATURN, longitude=0.01, speed=0.0)

    with pytest.raises(TypeError, match="requires timestamp_utc as UTCDateTime"):
        Snapshot.from_positions(timestamp_utc=ts, positions=[p_saturn]) # type: ignore


def test_snapshot_rejects_inconsistent_positions_map_key_vs_position_body() -> None:
    ts = UTCDateTime(datetime(2026, 2, 20, 16, 13, tzinfo=timezone.utc))
    p_saturn = Position(body=Body.SATURN, longitude=0.01, speed=0.0)

    with pytest.raises(ValueError, match="Inconsistent position map"):
        Snapshot(timestamp_utc=ts, positions_by_body={Body.NEPTUNE: p_saturn})


def test_snapshot_position_of_raises_for_missing_body() -> None:
    ts = UTCDateTime(datetime(2026, 2, 20, 16, 13, tzinfo=timezone.utc))

    p_saturn = Position(body=Body.SATURN, longitude=0.01, speed=0.0)
    snap = Snapshot.from_positions(timestamp_utc=ts, positions=[p_saturn])

    with pytest.raises(KeyError, match="Body not present in snapshot"):
        snap.position_of(Body.NEPTUNE)


def test_snapshot_timestamp_is_preserved_as_utcdatetime() -> None:
    ts = UTCDateTime(datetime(2026, 2, 20, 16, 13, tzinfo=timezone.utc))

    p_saturn = Position(body=Body.SATURN, longitude=0.01, speed=0.0)
    snap = Snapshot.from_positions(timestamp_utc=ts, positions=[p_saturn])

    assert isinstance(snap.timestamp_utc, UTCDateTime)
    assert snap.timestamp_utc == ts
    assert snap.timestamp_utc.dt.tzinfo == timezone.utc