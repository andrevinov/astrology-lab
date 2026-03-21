from datetime import datetime, timezone

import pytest

from astrolab.core.time.utc_types import UTCDateTime
from astrolab.domain.bodies import Body
from astrolab.domain.patterns.returns import ReturnEvent, detect_return
from astrolab.domain.positions import Position
from astrolab.domain.snapshots import Snapshot

TEST_TIMESTAMP = UTCDateTime(datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc))

def make_snapshot(*positions: Position) -> Snapshot:
    return Snapshot.from_positions(
        timestamp_utc=TEST_TIMESTAMP,
        positions=positions
    )


def test_detect_return_finds_exact_return():
    natal = make_snapshot(
        Position(body=Body.SUN, longitude=15.0, speed=1.0),
    )
    transit = make_snapshot(
        Position(body=Body.SUN, longitude=15.0, speed=0.98),
    )

    result = detect_return(natal, transit, body=Body.SUN, orb_deg=1.0)

    assert result == ReturnEvent(
        body=Body.SUN,
        separation_deg=0.0,
        orb_deg=0.0,
    )


def test_detect_return_finds_return_within_orb():
    natal = make_snapshot(
        Position(body=Body.SUN, longitude=15.0, speed=1.0),
    )
    transit = make_snapshot(
        Position(body=Body.SUN, longitude=15.6, speed=0.98),
    )

    result = detect_return(natal, transit, body=Body.SUN, orb_deg=1.0)

    assert result is not None
    assert result.body == Body.SUN
    assert result.separation_deg == pytest.approx(0.6)
    assert result.orb_deg == pytest.approx(0.6)


def test_detect_return_returns_none_outside_orb():
    natal = make_snapshot(
        Position(body=Body.SUN, longitude=15.0, speed=1.0),
    )
    transit = make_snapshot(
        Position(body=Body.SUN, longitude=17.0, speed=0.98),
    )

    result = detect_return(natal, transit, body=Body.SUN, orb_deg=1.0)

    assert result is None