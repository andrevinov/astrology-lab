# Claim Schema Specification

## Overview

The **claim schema** defines how astrological statements ("claims") are represented in a structured, reproducible, and testable way within the Astrolab project.

A claim describes **what should be verified**, not how to compute it. The computation is handled by domain logic, while the schema acts as a declarative input.

---

## Design Principles

* **Explicit inputs**: all parameters must be clearly defined
* **Reproducibility**: same input → same output
* **Separation of concerns**:

  * YAML → declaration
  * domain → computation
  * use_cases → orchestration
* **Extensibility**: new pattern types can be added without breaking existing ones

---

## Top-Level Structure

```yaml
claim:
  id: "string"
  title: "string"
  description: "string"
  source:
    video_title: "string"
    timestamp: "string"
  notes: "string"

pattern:
  kind: "string"
  params: {}

settings:
  orb_deg: float
  zodiac: "tropical" | "sidereal"
  ayanamsha: string | null
```

---

## Sections Explained

### 1. `claim`

Metadata describing the context of the claim.

| Field              | Description                            |
| ------------------ | -------------------------------------- |
| id                 | Unique identifier for the claim        |
| title              | Short human-readable description       |
| description        | Detailed explanation                   |
| source.video_title | Source reference                       |
| source.timestamp   | Timestamp in the source                |
| notes              | Optional observations or uncertainties |

---

### 2. `pattern`

Defines the **astrological structure** to be tested.

```yaml
pattern:
  kind: "transit_aspect"
  params: {}
```

The `kind` determines which domain detector will be used.

---

### 3. `settings`

Global parameters controlling how the pattern is evaluated.

| Field     | Description               |
| --------- | ------------------------- |
| orb_deg   | Maximum allowed orb       |
| zodiac    | Tropical or sidereal      |
| ayanamsha | Required only if sidereal |

---

## Supported Pattern Kinds (MVP)

### 1. Transit Aspect

Checks whether a transit body forms a specific aspect with a natal body.

```yaml
pattern:
  kind: "transit_aspect"
  params:
    transit_body: "MOON"
    natal_body: "MOON"
    aspect: "OPPOSITION"
```

Required fields:

* transit_body
* natal_body
* aspect

---

### 2. Return

Checks whether a body returns to its natal longitude.

```yaml
pattern:
  kind: "return"
  params:
    body: "SUN"
```

Required fields:

* body

---

### 3. Eclipse Trigger

Checks whether an eclipse point forms allowed aspects with a natal body.

```yaml
pattern:
  kind: "eclipse_trigger"
  params:
    eclipse_body: "SUN"
    natal_body: "MARS"
    allowed_aspects:
      - "CONJUNCTION"
      - "SQUARE"
      - "OPPOSITION"
```

Required fields:

* eclipse_body
* natal_body
* allowed_aspects

---

### 4. Midpoint Structure

Checks whether a transit body aspects the midpoint of two natal bodies.

```yaml
pattern:
  kind: "midpoint_structure"
  params:
    transit_body: "MARS"
    natal_body_a: "SUN"
    natal_body_b: "MOON"
    aspect: "CONJUNCTION"
```

Required fields:

* transit_body
* natal_body_a
* natal_body_b
* aspect

---

## Validation Rules

### Global Rules

* `claim.id` is required
* `pattern.kind` is required
* `pattern.params` is required
* `settings.orb_deg` is required
* `settings.zodiac` is required

### Conditional Rules

* `ayanamsha` must be provided if `zodiac == "sidereal"`

### Pattern-Specific Rules

| Pattern            | Required Fields                                  |
| ------------------ | ------------------------------------------------ |
| transit_aspect     | transit_body, natal_body, aspect                 |
| return             | body                                             |
| eclipse_trigger    | eclipse_body, natal_body, allowed_aspects        |
| midpoint_structure | transit_body, natal_body_a, natal_body_b, aspect |

---

## Example (Complete Claim)

```yaml
claim:
  id: "israel_moon_opposition_001"
  title: "Natal Moon opposed by transit Moon"
  description: "Verify whether the transit Moon opposes the natal Moon on the event date."
  source:
    video_title: "World Astrology Report"
    timestamp: "12:40-14:10"
  notes: "Base chart time may be uncertain."

pattern:
  kind: "transit_aspect"
  params:
    transit_body: "MOON"
    natal_body: "MOON"
    aspect: "OPPOSITION"

settings:
  orb_deg: 2.0
  zodiac: "tropical"
  ayanamsha: null
```

---

## Future Extensions

Potential additions:

* `ingress` (planet entering sign)
* `aspect_cluster` (e.g., T-square detection)
* `multi_pattern_claim` (composed conditions)
* `time_window_scan` (search across date ranges)

---

## Final Note

This schema is the foundation that allows Astrolab to:

* Translate narrative astrology into structured data
* Reproduce claims deterministically
* Compare occurrences across time
* Build a scalable analysis engine

The schema should remain **simple, explicit, and stable** as the system grows.
