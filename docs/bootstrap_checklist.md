# Initial Implementation Checklist

## Core

- [x] angles.py
- [x] orb.py
- [x] jd.py
- [ ] utc.py
- [ ] ranges.py

## Ephemeris

- [x] swisseph_adapter.py
- [ ] models.py

## Domain

- [x] bodies.py
- [x] positions.py
- [x] snapshots.py
- [ ] aspects.py
- [ ] charts.py

## Patterns

- [ ] transit_aspect.py (opposition only for MVP)

## Use Cases

- [ ] simulate_claim.py
- [ ] scan_transits.py (optional for MVP)

## IO

- [ ] inputs.py (parse case.yaml)
- [ ] outputs.py (result.json)
- [ ] report_md.py

## Cases

- [ ] case_0001 defined and runnable

## CLI

- [ ] basic CLI to run a case