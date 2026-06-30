# Architecture Decision Records (ADRs)

**Location:** `governance/adr/`
**Governed by:** [CONSTITUTION.md](../../CONSTITUTION.md) §7.1
**Standards hierarchy position:** Below Standards, above operational Playbooks

---

## Purpose

Architecture Decision Records capture significant architectural choices made during AEOS development. An ADR documents the context, the options considered, the decision made, and the consequences — so future contributors understand not just *what* was decided but *why*.

ADRs are immutable once accepted. If a decision is reversed, a new ADR supersedes the old one; the old ADR is marked superseded and remains in history.

---

## When to write an ADR

Write an ADR when:

- You are choosing between two or more plausible architectural approaches
- The decision is hard to reverse or has significant consequences
- Future contributors would reasonably wonder why this choice was made
- A decision introduces a new external dependency
- A decision changes the interface contract of a public API or CLI command

Do not write an ADR for:

- Routine bug fixes
- Documentation updates
- Decisions already captured in `CONSTITUTION.md` or `ARCHITECTURE.md`
- Implementation details that can be changed freely

---

## Format

File name: `ADR-NNN-short-title.md`

```markdown
# ADR-NNN — Short title

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Superseded by ADR-NNN | Withdrawn
**Deciders:** (names or roles)
**Capability:** Discover | Assess | Recover | Transform | Continue | Govern | Operate | Learn

## Context

What situation made this decision necessary. What problem are we solving.

## Options considered

### Option A — Name
Description. Pros. Cons.

### Option B — Name
Description. Pros. Cons.

## Decision

What was decided, in one sentence.

## Rationale

Why this option was chosen over the alternatives.

## Consequences

What this decision implies going forward. What becomes easier. What becomes harder.
What we commit to maintaining.

## Links

- Related ADR: ADR-NNN
- Related RFC: RFC-NNN
- Related Standard: governance/standards/
```

---

## Process

1. **Author** writes the ADR as a PR
2. **Review** — at least one other contributor reviews context and rationale
3. **Accepted** — merged with status "Accepted"
4. **Superseded** — if reversed, new ADR references old; old is updated to "Superseded by ADR-NNN"

No ADR may contradict `MANIFESTO.md` or `CONSTITUTION.md`. ADRs that would require a constitutional change must go through the RFC process first.

---

## Numbering

ADRs are numbered sequentially: `ADR-001`, `ADR-002`, etc. Numbers are never reused.
