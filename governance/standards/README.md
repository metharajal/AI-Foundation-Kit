# AEOS Standards

**Location:** `governance/standards/`
**Governed by:** [CONSTITUTION.md](../../CONSTITUTION.md) §7.1–7.3
**Standards hierarchy position:** Below Constitution, above Playbooks and ADRs

---

## Purpose

Standards define *how* AEOS implements its constitutional principles in concrete, repeatable ways. Where the Constitution states *what* must be true (the invariants and principles), Standards define *how* those invariants are achieved in practice.

Standards apply to:
- Code patterns and module structure
- CLI interface design conventions
- Data model design (MemoryRecord, EvidenceReport, etc.)
- Test structure and coverage requirements
- Documentation format and completeness
- Engine design contracts

---

## Standards hierarchy

```
MANIFESTO.md           ← supreme, immutable
CONSTITUTION.md        ← identity and invariants
governance/standards/  ← implementation standards  ← you are here
governance/playbooks/  ← operational procedures
governance/adr/        ← individual architecture decisions
```

A Standard must not contradict the Constitution. A Standard that would require a constitutional change must go through an RFC first.

---

## When to write a Standard

Write a Standard when:

- A pattern is used consistently across multiple modules and should be enforced
- A new type of component (command, engine, output model) needs a design contract
- A quality requirement needs to be specified precisely enough to be testable
- A convention is important enough that deviations should require explicit justification

Do not write a Standard for:

- One-time implementation decisions (use ADR instead)
- Operational procedures for a specific task (use Playbook instead)
- Constitutional-level invariants (already in CONSTITUTION.md)

---

## Format

File name: `STD-NNN-short-title.md`

```markdown
# STD-NNN — Short title

**Date:** YYYY-MM-DD
**Status:** Draft | Active | Deprecated | Superseded by STD-NNN
**Scope:** CLI | Engine | Data Model | Testing | Documentation | Agent
**Governed by:** CONSTITUTION.md §X.Y

## Standard

What is required. Write as "MUST", "SHOULD", "MUST NOT" statements.

## Rationale

Why this standard exists.

## Examples

Compliant example (code or structure).

Non-compliant example (what to avoid).

## Exceptions

When is it acceptable to deviate from this standard.
Exceptions must be documented in an ADR.

## Verification

How compliance is verified (test, lint rule, code review checklist).
```

---

## Active Standards

*(None yet — to be added as AEOS matures)*

---

## Numbering

Standards are numbered sequentially: `STD-001`, `STD-002`, etc. Numbers are never reused.
