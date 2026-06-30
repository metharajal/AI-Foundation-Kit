# Decisions (DEC)

**Location:** `governance/dec/`
**Governed by:** [CONSTITUTION.md](../../CONSTITUTION.md) §7.1

---

## Purpose

The `governance/dec/` directory stores formal decision records that result from ratified RFCs or significant governance choices that are not architecture-level (which would go in `governance/adr/`).

DECs capture:
- Constitutional amendments
- Capability additions or removals
- Engine additions or removals
- Interface contract changes
- Standards adoptions
- Strategic direction changes

The decision log at `docs/DECISIONS.md` is the human-readable narrative. DEC files here are the formal governance artifacts that may reference specific RFC(s) and ADR(s).

---

## Relationship to other governance artifacts

```
RFC-NNN (proposal)
    → reviewed and accepted
    → DEC-NNN (ratified decision)
    → ADR-NNN (architectural consequence, if applicable)
    → CONSTITUTION.md update (if constitutional amendment)
```

Not every DEC requires an RFC. Decisions within existing constitutional bounds may go directly to a DEC after review.

---

## Format

File name: `DEC-NNN-short-title.md`

```markdown
# DEC-NNN — Short title

**Date:** YYYY-MM-DD
**Status:** Ratified | Superseded by DEC-NNN | Withdrawn
**RFC:** RFC-NNN (if applicable)
**Category:** Constitutional | Capability | Engine | Interface | Standards | Strategic

## Decision

What was decided, precisely.

## Context

Why this decision was needed.

## Rationale

Why this is the right decision.

## Consequences

What this decision commits AEOS to.

## Related

- RFC-NNN
- ADR-NNN
- docs/DECISIONS.md#DEC-NNN
```

---

## Numbering

DECs are numbered sequentially: `DEC-001`, `DEC-002`, etc. Numbers are never reused.

The numbering space for DEC is shared with `docs/DECISIONS.md`. DEC-001 through DEC-010 correspond to the ten decisions recorded at project inception in `docs/DECISIONS.md`.
