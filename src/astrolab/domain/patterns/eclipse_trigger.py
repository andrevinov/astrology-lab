from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from astrolab.core.math.angles import norm360
from astrolab.domain.aspects import Aspect, angular_separation
from astrolab.domain.bodies import Body
from astrolab.domain.snapshots import Snapshot


@dataclass(frozen=True)
class EclipseTriggerEvent:
    """
    A detected transit activation of a previously known eclipse degree.

    Example:
    - transit Mars conjunct eclipse degree at 15 Aries
    - transit Saturn square eclipse degree at 22 Libra
    """

    transit_body: Body
    eclipse_longitude: float
    aspect: Aspect
    separation_deg: float
    orb_deg: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "eclipse_longitude", norm360(self.eclipse_longitude))


def detect_eclipse_triggers(
    transit_snapshot: Snapshot,
    eclipse_longitude: float,
    orb_deg: float,
    *,
    transit_bodies: Iterable[Body] | None = None,
    allowed_aspects: Iterable[Aspect] | None = None,
) -> tuple[EclipseTriggerEvent, ...]:
    """
    Detect transit activations of a known eclipse degree.

    Rules:
    - compares each selected transit body against the eclipse longitude
    - uses a single global orb
    - if multiple aspects are possible, returns the closest exact match
    - output is sorted for deterministic results
    """
    if orb_deg < 0.0:
        raise ValueError("orb_deg must be non-negative")

    normalized_eclipse_longitude = norm360(eclipse_longitude)
    selected_transit_bodies = _resolve_bodies(
        requested=transit_bodies,
        available=transit_snapshot.bodies,
    )
    selected_aspects = _resolve_aspects(allowed_aspects)

    hits: list[EclipseTriggerEvent] = []

    for transit_body in selected_transit_bodies:
        transit_position = transit_snapshot.position_of(transit_body)

        separation_deg = angular_separation(
            transit_position.longitude,
            normalized_eclipse_longitude,
        )

        aspect = _detect_allowed_aspect(
            separation_deg=separation_deg,
            orb_deg=orb_deg,
            allowed_aspects=selected_aspects,
        )
        if aspect is None:
            continue

        hits.append(
            EclipseTriggerEvent(
                transit_body=transit_body,
                eclipse_longitude=normalized_eclipse_longitude,
                aspect=aspect,
                separation_deg=separation_deg,
                orb_deg=abs(separation_deg - aspect.angle),
            )
        )

    return tuple(sorted(hits, key=_sort_key))


def _resolve_bodies(
    *,
    requested: Iterable[Body] | None,
    available: Iterable[Body],
) -> tuple[Body, ...]:
    if requested is None:
        return tuple(available)

    available_set = set(available)
    resolved = tuple(dict.fromkeys(requested))

    missing = [body for body in resolved if body not in available_set]
    if missing:
        missing_names = ", ".join(body.name for body in missing)
        raise ValueError(f"Requested bodies are not present in snapshot: {missing_names}")

    return resolved


def _resolve_aspects(allowed_aspects: Iterable[Aspect] | None) -> tuple[Aspect, ...]:
    if allowed_aspects is None:
        return tuple(Aspect)

    resolved = tuple(dict.fromkeys(allowed_aspects))
    if not resolved:
        raise ValueError("allowed_aspects must not be empty")

    return resolved


def _detect_allowed_aspect(
    *,
    separation_deg: float,
    orb_deg: float,
    allowed_aspects: tuple[Aspect, ...],
) -> Aspect | None:
    best_match: Aspect | None = None
    best_distance: float | None = None

    for aspect in allowed_aspects:
        distance = abs(separation_deg - aspect.angle)
        if distance <= orb_deg:
            if best_distance is None or distance < best_distance:
                best_match = aspect
                best_distance = distance

    return best_match


def _sort_key(hit: EclipseTriggerEvent) -> tuple[float, str, float]:
    return (
        hit.orb_deg,
        hit.transit_body.value,
        hit.aspect.angle,
    )