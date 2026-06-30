# Request for Comments (RFCs)

**Location:** `governance/rfc/`
**Governed by:** [CONSTITUTION.md](../../CONSTITUTION.md) §8.1, §7.1

---

## Purpose

RFCs are the process for proposing significant changes to AEOS that require broader consideration than a standard ADR. They are used for:

- Constitutional amendments (CONSTITUTION §8.1)
- New platform capabilities (additions to the 8 canonical capabilities)
- New platform engines (additions to the 10 engines)
- New external dependencies with sovereignty implications
- Changes to public CLI interface contracts
- Changes to the Standards hierarchy

RFCs are proposals, not decisions. An RFC that goes through the process and is ratified becomes a decision (recorded in `governance/dec/`) or a constitutional amendment.

---

## When to write an RFC

Write an RFC when:

- The change would modify `CONSTITUTION.md`
- The change introduces a capability, engine, or interface not currently defined
- The change adds a non-trivial external dependency
- The change affects the CLI interface contract in a breaking way
- The change requires coordination across multiple contributors

Do not write an RFC for:

- Bug fixes, even significant ones
- Documentation improvements
- ADR-level architecture decisions within existing constraints
- Implementation changes that do not affect public contracts

---

## Format

File name: `RFC-NNN-short-title.md`

```markdown
# RFC-NNN — Short title

**Date:** YYYY-MM-DD
**Status:** Draft | Under Review | Accepted | Rejected | Withdrawn
**Author:** (name or role)
**Category:** Constitutional | Capability | Engine | Interface | Dependency | Standards

## Summary

One paragraph: what is being proposed and why.

## Motivation

What problem does this solve. Why is the current state insufficient.

## Detailed design

What exactly is being changed. Be specific about interfaces, data structures,
behavior, and invariants.

## Drawbacks

What are the risks and costs of this change.

## Alternatives

What other approaches were considered. Why were they rejected.

## Sovereignty impact

How does this affect AEOS's own sovereignty posture.
New dependencies must include an exit strategy.

## Unresolved questions

What needs to be decided before this RFC can be accepted.

## Implementation plan

How will this be implemented if accepted. Which sprints or milestones.
```

---

## Process

1. **Author** opens an RFC as a PR with status "Draft"
2. **Discussion period** — minimum 1 week for non-trivial RFCs
3. **Revision** — author updates based on feedback
4. **Review** — at least one core contributor reviews
5. **Decision** — RFC is marked "Accepted" or "Rejected" with rationale
6. **Implementation** — if accepted, create ADR(s) and/or DEC entry
7. **Constitutional amendment** — if applicable, update `CONSTITUTION.md` with version bump

No RFC may contradict `MANIFESTO.md`. An RFC that would require modifying a Manifesto article is rejected.

---

## Numbering

RFCs are numbered sequentially: `RFC-001`, `RFC-002`, etc. Numbers are never reused.
