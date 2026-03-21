from __future__ import annotations

from datetime import datetime, timezone

import pytest

from astrolab.core.time.utc_types import UTCDateTime
from astrolab.domain.aspects import Aspect
from astrolab.domain.bodies import Body
from astrolab.domain.patterns.transit_aspect import TransitAspect, detect_transit_aspects
from astrolab.domain.positions import Position
from astrolab.domain.snapshots import Snapshot

TEST_TIMESTAMP = UTCDateTime(datetime(2026, 2, 20, 16, 13, tzinfo=timezone.utc))

def make_snapshot(*positions: Position) -> Snapshot:
    return Snapshot.from_positions(
        timestamp_utc=TEST_TIMESTAMP,
        positions=positions,
    )

def test_detect_transit_aspects_finds_conjunction():
    natal = make_snapshot(
        Position(body=Body.MOON, longitude=60.0, speed=13.0),
    )
    transit = make_snapshot(
        Position(body=Body.MERCURY, longitude=60.0, speed=1.2),
    )

    result = detect_transit_aspects(natal, transit, orb_deg=1.0)

    assert result == (
        TransitAspect(
            transit_body=Body.MERCURY,
            natal_body=Body.MOON,
            aspect=Aspect.CONJUNCTION,
            separation_deg=0.0,
            orb_deg=0.0,
        ),
    )


def test_detect_transit_aspects_finds_square():
    natal = make_snapshot(
        Position(body=Body.MOON, longitude=60.0, speed=13.0),
    )
    transit = make_snapshot(
        Position(body=Body.SATURN, longitude=150.0, speed=0.05),
    )

    result = detect_transit_aspects(natal, transit, orb_deg=2.0)

    assert len(result) == 1
    assert result[0].transit_body is Body.SATURN
    assert result[0].natal_body is Body.MOON
    assert result[0].aspect is Aspect.SQUARE
    assert result[0].separation_deg == 90.0
    assert result[0].orb_deg == 0.0


def test_detect_transit_aspects_returns_empty_tuple_when_no_match():
    natal = make_snapshot(
        Position(body=Body.MOON, longitude=60.0, speed=13.0),
    )
    transit = make_snapshot(
        Position(body=Body.MERCURY, longitude=80.0, speed=1.2),
    )

    result = detect_transit_aspects(natal, transit, orb_deg=3.0)

    assert result == ()


def test_detect_transit_aspects_checks_all_transit_and_natal_pairs():
    natal = make_snapshot(
        Position(body=Body.MOON, longitude=60.0, speed=13.0),
        Position(body=Body.SUN, longitude=10.0, speed=1.0),
    )
    transit = make_snapshot(
        Position(body=Body.MERCURY, longitude=60.0, speed=1.2),
        Position(body=Body.JUPITER, longitude=190.0, speed=0.08),
    )

    result = detect_transit_aspects(natal, transit, orb_deg=2.0)

    assert len(result) == 2

    assert result[0].transit_body is Body.JUPITER
    assert result[0].natal_body is Body.SUN
    assert result[0].aspect is Aspect.OPPOSITION

    assert result[1].transit_body is Body.MERCURY
    assert result[1].natal_body is Body.MOON
    assert result[1].aspect is Aspect.CONJUNCTION


def test_detect_transit_aspects_can_filter_bodies():
    natal = make_snapshot(
        Position(body=Body.MOON, longitude=60.0, speed=13.0),
        Position(body=Body.SUN, longitude=10.0, speed=1.0),
    )
    transit = make_snapshot(
        Position(body=Body.MERCURY, longitude=60.0, speed=1.2),
        Position(body=Body.JUPITER, longitude=190.0, speed=0.08),
    )

    result = detect_transit_aspects(
        natal,
        transit,
        orb_deg=2.0,
        natal_bodies=(Body.MOON,),
        transit_bodies=(Body.MERCURY,),
    )

    assert len(result) == 1
    assert result[0].transit_body is Body.MERCURY
    assert result[0].natal_body is Body.MOON
    assert result[0].aspect is Aspect.CONJUNCTION


def test_detect_transit_aspects_can_filter_allowed_aspects():
    natal = make_snapshot(
        Position(body=Body.MOON, longitude=60.0, speed=13.0),
    )
    transit = make_snapshot(
        Position(body=Body.SATURN, longitude=150.0, speed=0.05),
    )

    result = detect_transit_aspects(
        natal,
        transit,
        orb_deg=2.0,
        allowed_aspects=(Aspect.TRINE,),
    )

    assert result == ()


def test_detect_transit_aspects_raises_for_negative_orb():
    natal = make_snapshot(
        Position(body=Body.MOON, longitude=60.0, speed=13.0),
    )
    transit = make_snapshot(
        Position(body=Body.MERCURY, longitude=60.0, speed=1.2),
    )

    with pytest.raises(ValueError, match="orb_deg must be non-negative"):
        detect_transit_aspects(natal, transit, orb_deg=-1.0)


def test_detect_transit_aspects_raises_for_missing_requested_body():
    natal = make_snapshot(
        Position(body=Body.MOON, longitude=60.0, speed=13.0),
    )
    transit = make_snapshot(
        Position(body=Body.MERCURY, longitude=60.0, speed=1.2),
    )

    with pytest.raises(ValueError, match="Requested bodies are not present in snapshot"):
        detect_transit_aspects(
            natal,
            transit,
            orb_deg=1.0,
            natal_bodies=(Body.SUN,),
        )


def test_detect_transit_aspects_raises_for_empty_allowed_aspects():
    natal = make_snapshot(
        Position(body=Body.MOON, longitude=60.0, speed=13.0),
    )
    transit = make_snapshot(
        Position(body=Body.MERCURY, longitude=60.0, speed=1.2),
    )

    with pytest.raises(ValueError, match="allowed_aspects must not be empty"):
        detect_transit_aspects(
            natal,
            transit,
            orb_deg=1.0,
            allowed_aspects=(),
        )


def test_detect_transit_aspects_picks_closest_aspect_when_orb_overlaps():
    natal = make_snapshot(
        Position(body=Body.MOON, longitude=0.0, speed=13.0),
    )
    transit = make_snapshot(
        Position(body=Body.MERCURY, longitude=80.0, speed=1.2),
    )

    result = detect_transit_aspects(
        natal,
        transit,
        orb_deg=25.0,
        allowed_aspects=(Aspect.SQUARE, Aspect.TRINE),
    )

    assert len(result) == 1
    assert result[0].aspect is Aspect.SQUARE
    assert result[0].separation_deg == 80.0
    assert result[0].orb_deg == 10.0