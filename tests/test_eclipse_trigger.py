import math
from datetime import datetime, timezone

from astrolab.core.time.utc_types import UTCDateTime
from astrolab.domain.aspects import Aspect
from astrolab.domain.bodies import Body
from astrolab.domain.patterns.eclipse_trigger import (
    EclipseTriggerEvent,
    detect_eclipse_triggers,
)
from astrolab.domain.positions import Position
from astrolab.domain.snapshots import Snapshot


def dt(hours: int = 0) -> UTCDateTime:
    return UTCDateTime(datetime(2024, 1, 1, hours, 0, 0, tzinfo=timezone.utc))


def make_snapshot(*positions: Position) -> Snapshot:
    return Snapshot.from_positions(
        timestamp_utc=dt(),
        positions=positions,
    )


def assert_close(a: float, b: float, tol: float = 1e-9) -> None:
    assert math.isclose(a, b, abs_tol=tol)


def assert_trigger(
    actual: EclipseTriggerEvent,
    *,
    transit_body: Body,
    eclipse_longitude: float,
    aspect: Aspect,
    separation_deg: float,
    orb_deg: float,
) -> None:
    assert actual.transit_body == transit_body
    assert_close(actual.eclipse_longitude, eclipse_longitude)
    assert actual.aspect == aspect
    assert_close(actual.separation_deg, separation_deg)
    assert_close(actual.orb_deg, orb_deg)


def test_detect_eclipse_trigger_by_conjunction():
    transit = make_snapshot(
        Position(body=Body.MARS, longitude=15.4, speed=0.7),
    )

    result = detect_eclipse_triggers(
        transit_snapshot=transit,
        eclipse_longitude=15.0,
        orb_deg=1.0,
    )

    assert len(result) == 1
    assert_trigger(
        result[0],
        transit_body=Body.MARS,
        eclipse_longitude=15.0,
        aspect=Aspect.CONJUNCTION,
        separation_deg=0.4,
        orb_deg=0.4,
    )


def test_detect_eclipse_trigger_by_square():
    transit = make_snapshot(
        Position(body=Body.SATURN, longitude=104.2, speed=0.1),
    )

    result = detect_eclipse_triggers(
        transit_snapshot=transit,
        eclipse_longitude=15.0,
        orb_deg=1.0,
    )

    assert len(result) == 1
    assert_trigger(
        result[0],
        transit_body=Body.SATURN,
        eclipse_longitude=15.0,
        aspect=Aspect.SQUARE,
        separation_deg=89.2,
        orb_deg=0.8,
    )


def test_detect_eclipse_trigger_returns_empty_when_no_hit():
    transit = make_snapshot(
        Position(body=Body.JUPITER, longitude=40.0, speed=0.2),
    )

    result = detect_eclipse_triggers(
        transit_snapshot=transit,
        eclipse_longitude=15.0,
        orb_deg=1.0,
    )

    assert result == ()


def test_detect_eclipse_trigger_filters_bodies():
    transit = make_snapshot(
        Position(body=Body.MARS, longitude=15.4, speed=0.7),
        Position(body=Body.VENUS, longitude=15.2, speed=1.1),
    )

    result = detect_eclipse_triggers(
        transit_snapshot=transit,
        eclipse_longitude=15.0,
        orb_deg=1.0,
        transit_bodies=(Body.VENUS,),
    )

    assert len(result) == 1
    assert_trigger(
        result[0],
        transit_body=Body.VENUS,
        eclipse_longitude=15.0,
        aspect=Aspect.CONJUNCTION,
        separation_deg=0.2,
        orb_deg=0.2,
    )


def test_detect_eclipse_trigger_filters_allowed_aspects():
    transit = make_snapshot(
        Position(body=Body.MARS, longitude=15.4, speed=0.7),
        Position(body=Body.SATURN, longitude=104.2, speed=0.1),
    )

    result = detect_eclipse_triggers(
        transit_snapshot=transit,
        eclipse_longitude=15.0,
        orb_deg=1.0,
        allowed_aspects=(Aspect.SQUARE,),
    )

    assert len(result) == 1
    assert_trigger(
        result[0],
        transit_body=Body.SATURN,
        eclipse_longitude=15.0,
        aspect=Aspect.SQUARE,
        separation_deg=89.2,
        orb_deg=0.8,
    )


def test_detect_eclipse_trigger_rejects_negative_orb():
    transit = make_snapshot(
        Position(body=Body.MARS, longitude=15.0, speed=0.7),
    )

    try:
        detect_eclipse_triggers(
            transit_snapshot=transit,
            eclipse_longitude=15.0,
            orb_deg=-1.0,
        )
        assert False, "Expected ValueError for negative orb"
    except ValueError as exc:
        assert str(exc) == "orb_deg must be non-negative"


def test_detect_eclipse_trigger_rejects_missing_requested_body():
    transit = make_snapshot(
        Position(body=Body.MARS, longitude=15.0, speed=0.7),
    )

    try:
        detect_eclipse_triggers(
            transit_snapshot=transit,
            eclipse_longitude=15.0,
            orb_deg=1.0,
            transit_bodies=(Body.VENUS,),
        )
        assert False, "Expected ValueError for missing requested body"
    except ValueError as exc:
        assert str(exc) == "Requested bodies are not present in snapshot: VENUS"


def test_detect_eclipse_trigger_rejects_empty_allowed_aspects():
    transit = make_snapshot(
        Position(body=Body.MARS, longitude=15.0, speed=0.7),
    )

    try:
        detect_eclipse_triggers(
            transit_snapshot=transit,
            eclipse_longitude=15.0,
            orb_deg=1.0,
            allowed_aspects=(),
        )
        assert False, "Expected ValueError for empty allowed_aspects"
    except ValueError as exc:
        assert str(exc) == "allowed_aspects must not be empty"


def test_detect_eclipse_trigger_normalizes_eclipse_longitude():
    transit = make_snapshot(
        Position(body=Body.MARS, longitude=0.3, speed=0.7),
    )

    result = detect_eclipse_triggers(
        transit_snapshot=transit,
        eclipse_longitude=360.0,
        orb_deg=1.0,
    )

    assert len(result) == 1
    assert_trigger(
        result[0],
        transit_body=Body.MARS,
        eclipse_longitude=0.0,
        aspect=Aspect.CONJUNCTION,
        separation_deg=0.3,
        orb_deg=0.3,
    )


def test_detect_eclipse_trigger_is_sorted_deterministically():
    transit = make_snapshot(
        Position(body=Body.VENUS, longitude=15.5, speed=1.0),
        Position(body=Body.MARS, longitude=15.2, speed=0.7),
        Position(body=Body.SATURN, longitude=104.6, speed=0.1),
    )

    result = detect_eclipse_triggers(
        transit_snapshot=transit,
        eclipse_longitude=15.0,
        orb_deg=1.0,
    )

    assert len(result) == 3

    assert_trigger(
        result[0],
        transit_body=Body.MARS,
        eclipse_longitude=15.0,
        aspect=Aspect.CONJUNCTION,
        separation_deg=0.2,
        orb_deg=0.2,
    )
    assert_trigger(
        result[1],
        transit_body=Body.SATURN,
        eclipse_longitude=15.0,
        aspect=Aspect.SQUARE,
        separation_deg=89.6,
        orb_deg=0.4,
    )
    assert_trigger(
        result[2],
        transit_body=Body.VENUS,
        eclipse_longitude=15.0,
        aspect=Aspect.CONJUNCTION,
        separation_deg=0.5,
        orb_deg=0.5,
    )