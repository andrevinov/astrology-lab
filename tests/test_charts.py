# tests/test_charts.py
#
# Unit tests for the Chart domain entity.
#
# This module validates that Chart:
#
# 1. Wraps a Snapshot with chart-level metadata
# 2. Exposes timestamp, bodies, and positions from the underlying snapshot
# 3. Delegates body lookup helpers correctly
# 4. Normalizes string metadata during initialization
# 5. Rejects invalid chart inputs

from datetime import datetime, timezone

from astrolab.core.time.utc_types import UTCDateTime
from astrolab.domain.bodies import Body
from astrolab.domain.charts import Chart
from astrolab.domain.positions import Position
from astrolab.domain.snapshots import Snapshot


def make_snapshot() -> Snapshot:
    """
    Build a small reusable snapshot fixture for chart tests.

    We keep this local helper intentionally simple so each test
    can focus on Chart behavior rather than Snapshot construction.
    """
    
    timestamp = UTCDateTime(
        datetime(2026, 3, 20, 12, 0, 0, tzinfo=timezone.utc)
    )

    positions = [
        Position(body=Body.SUN, longitude=0.0, speed=1.0),
        Position(body=Body.MOON, longitude=15.0, speed=13.2),
        Position(body=Body.SATURN, longitude=330.0, speed=0.05),
    ]

    return Snapshot.from_positions(timestamp_utc=timestamp, positions=positions)


# ==========================================================
# Basic construction
# ==========================================================

def test_chart_can_be_created_from_snapshot():
    """
    A Chart should accept a valid Snapshot and preserve
    the explicitly provided chart metadata.
    """
    snapshot = make_snapshot()

    chart = Chart(
        snapshot=snapshot,
        name="André Natal Chart",
        chart_type="natal",
        zodiac="tropical",
        notes="Reference chart.",
    )

    assert chart.snapshot is snapshot
    assert chart.name == "André Natal Chart"
    assert chart.chart_type == "natal"
    assert chart.zodiac == "tropical"
    assert chart.notes == "Reference chart."


# ==========================================================
# Snapshot passthrough properties
# ==========================================================

def test_chart_exposes_timestamp_from_snapshot():
    """
    Chart.timestamp_utc should be forwarded directly
    from the underlying snapshot.
    """
    snapshot = make_snapshot()
    chart = Chart(snapshot=snapshot)

    assert chart.timestamp_utc == snapshot.timestamp_utc


def test_chart_exposes_bodies_from_snapshot():
    """
    Chart.bodies should mirror the bodies available
    in the wrapped snapshot.
    """
    snapshot = make_snapshot()
    chart = Chart(snapshot=snapshot)

    assert chart.bodies == snapshot.bodies


def test_chart_exposes_positions_from_snapshot():
    """
    Chart.positions should mirror the positions stored
    in the wrapped snapshot.
    """
    snapshot = make_snapshot()
    chart = Chart(snapshot=snapshot)

    assert chart.positions == snapshot.positions


# ==========================================================
# Delegation helpers
# ==========================================================

def test_chart_has_body_delegates_to_snapshot():
    """
    Chart.has_body should return the same result
    as the underlying snapshot helper.
    """
    chart = Chart(snapshot=make_snapshot())

    assert chart.has_body(Body.SUN) is True
    assert chart.has_body(Body.JUPITER) is False


def test_chart_position_of_returns_position_from_snapshot():
    """
    Chart.position_of should return the exact Position
    stored for the requested body.
    """
    chart = Chart(snapshot=make_snapshot())

    position = chart.position_of(Body.MOON)

    assert position.body is Body.MOON
    assert position.longitude == 15.0
    assert position.speed == 13.2


def test_chart_position_of_raises_for_missing_body():
    """
    Requesting a body not present in the chart should
    propagate the snapshot error.
    """
    chart = Chart(snapshot=make_snapshot())

    try:
        chart.position_of(Body.JUPITER)
        assert False, "Expected KeyError for missing body."
    except KeyError as exc:
        assert "Body not present in snapshot" in str(exc)


# ==========================================================
# Metadata normalization
# ==========================================================

def test_chart_normalizes_chart_type_and_zodiac():
    """
    chart_type should be stripped, and zodiac should be
    stripped and normalized to lowercase.
    """
    chart = Chart(
        snapshot=make_snapshot(),
        chart_type="  natal  ",
        zodiac="  Tropical  ",
    )

    assert chart.chart_type == "natal"
    assert chart.zodiac == "tropical"


def test_chart_normalizes_blank_name_to_none():
    """
    A name containing only whitespace should be normalized to None.
    """
    chart = Chart(
        snapshot=make_snapshot(),
        name="   ",
    )

    assert chart.name is None


def test_chart_normalizes_blank_notes_to_none():
    """
    Notes containing only whitespace should be normalized to None.
    """
    chart = Chart(
        snapshot=make_snapshot(),
        notes="   ",
    )

    assert chart.notes is None


# ==========================================================
# Validation
# ==========================================================

def test_chart_rejects_non_snapshot_input():
    """
    Chart must receive a real Snapshot instance.
    """
    try:
        Chart(snapshot="not a snapshot")  # type: ignore[arg-type]
        assert False, "Expected TypeError for invalid snapshot."
    except TypeError as exc:
        assert "Chart.snapshot must be a Snapshot instance." in str(exc)


def test_chart_rejects_blank_chart_type():
    """
    chart_type must remain a meaningful non-empty string
    after trimming whitespace.
    """
    try:
        Chart(snapshot=make_snapshot(), chart_type="   ")
        assert False, "Expected ValueError for blank chart_type."
    except ValueError as exc:
        assert "Chart.chart_type must be a non-empty string." in str(exc)


def test_chart_rejects_blank_zodiac():
    """
    zodiac must remain a meaningful non-empty string
    after trimming whitespace.
    """
    try:
        Chart(snapshot=make_snapshot(), zodiac="   ")
        assert False, "Expected ValueError for blank zodiac."
    except ValueError as exc:
        assert "Chart.zodiac must be a non-empty string." in str(exc)