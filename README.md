# Astrolab

Astrolab is a technical astrology lab designed to **study, reproduce, and validate astrological claims through code**.

This project sits at the intersection of:

- Astrology (technical, structured, reproducible)
- Software Engineering (Clean Architecture, testability, determinism)
- Scientific thinking (explicit inputs, repeatable results, documented limitations)

The goal is not belief — it is **reproducibility**.

---

## Core Idea

Instead of consuming astrological interpretations passively, Astrolab:

1. Extracts a **technical claim** from an astrologer (e.g. “transit Moon opposed natal Moon”)
2. Reconstructs the exact scenario using ephemeris data
3. Verifies if the claim is **computationally valid**
4. Generalizes the pattern across time (past and future)
5. Documents everything in a reproducible format

Each case becomes a **unit of knowledge + code + evidence**.

---

## What This Project Is

- A **laboratory** for studying astrology through computation
- A **clean architecture Python project**
- A **portfolio project** demonstrating:
  - domain modeling
  - deterministic systems
  - reproducible pipelines
- A growing **dataset of astrological cases**

---

## What This Project Is NOT

- Not an astrology app for end users
- Not focused on UI/UX
- Not interpretative astrology inside the core logic
- Not dependent on external APIs (Swiss Ephemeris only)

---

## Tech Stack

- Python
- Swiss Ephemeris (`pyswisseph`)
- Pytest (testing)
- Ruff / Black (formatting)

Optional:
- Kerykeion / Flatlib (only if useful, never core dependency)

---

## Architecture

The project follows a **Clean Architecture-inspired structure**:

```

src/astrolab/

core/        # pure math, time, and deterministic calculations
ephemeris/   # Swiss Ephemeris adapter
domain/      # astrology concepts (bodies, aspects, patterns)
use_cases/   # orchestration (simulate, scan, reproduce)
io/          # inputs, outputs, reports

tests/       # unit tests
cases/       # reproducible astrological cases

```

### Principles

- Core logic must be **pure and deterministic**
- Domain defines **what things are**
- Use cases define **what the system does**
- IO handles **serialization only**
- Interpretation NEVER enters core

---

## Reproducibility Standard

Every astrological case must include:

- Explicit inputs:
  - UTC datetime
  - location (if needed)
  - orb definition
  - zodiac type
- A `case.yaml`
- Generated artifacts:
  - `result.json`
  - `report.md`
- Ability to rerun and obtain **the same result**

---

## Example Workflow

1. Select a claim from a video (e.g. World Astrology Report)
2. Define inputs (entity, date, location)
3. Compute planetary positions
4. Detect the pattern (aspect, return, midpoint, etc.)
5. Validate:
   - Did it happen?
   - With what orb?
   - At what exact time?
6. Scan for other occurrences
7. Document the case

---

## Current Capabilities (initial)

- Julian Day conversions
- Angle normalization
- Orb calculations
- Swiss Ephemeris integration
- Aspect detection (in progress)

---

## Running the Project

### Install dependencies

```

pip install -r requirements.txt

```

### Run tests

```

pytest

```

### Run a case (example)

```

python -m astrolab.use_cases.simulate_claim cases/case_0001_.../case.yaml

```

---

## Design Philosophy

Astrolab treats astrology as a **pattern detection problem over time**.

The system focuses on:

- precision over interpretation
- structure over narrative
- reproducibility over authority

Interpretation is allowed — but only **after the data is validated**.

---

## Future Directions

- Transit scanning engine
- Midpoint structures
- Eclipse triggers
- Chart rendering (SVG)
- Statistical analysis of patterns

---

## Why This Exists

Most astrology is:

- hard to verify
- loosely defined
- dependent on authority

Astrolab exists to ask:

> “Can this claim be computed, verified, and reproduced?”

If yes — it becomes knowledge.

If not — it becomes hypothesis.

---

## License

MIT