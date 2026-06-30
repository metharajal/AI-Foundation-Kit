# AEOS Playbooks

**Location:** `governance/playbooks/`
**Governed by:** [CONSTITUTION.md](../../CONSTITUTION.md) §7.2
**Standards hierarchy position:** Below Standards — operational procedures

---

## Purpose

Playbooks are step-by-step procedures for repeatable operational tasks. Where Standards define *what must be true*, Playbooks define *how to do it* in a specific situation.

Playbooks are used for:
- Release procedures
- Incident response
- Dependency upgrades
- New contributor onboarding
- Client project recovery (template)
- Security incident handling

---

## Standards hierarchy

```
MANIFESTO.md           ← supreme, immutable
CONSTITUTION.md        ← identity and invariants
governance/standards/  ← implementation standards
governance/playbooks/  ← operational procedures  ← you are here
governance/adr/        ← individual architecture decisions
```

---

## When to write a Playbook

Write a Playbook when:

- A task is performed repeatedly and mistakes are costly
- A task has a defined correct sequence that is not obvious
- A task involves multiple people or systems and coordination matters
- A task is security-sensitive and must not be improvised

Do not write a Playbook for:

- Architecture decisions (use ADR instead)
- One-time tasks
- Tasks already fully covered by automated tooling

---

## Playbook format (CONSTITUTION §7.2)

Every Playbook must include these seven sections:

```markdown
# PB-NNN — Short title

**Version:** 1.0.0
**Status:** Active | Draft | Deprecated
**Owner:** (role, not person)
**Last reviewed:** YYYY-MM-DD

## 1. Purpose
What this playbook is for. When to use it.

## 2. Prerequisites
What must be true before starting. Tools, permissions, states.

## 3. Steps
Numbered, precise steps. Each step has a clear action and expected outcome.

## 4. Verification
How to confirm the procedure succeeded.

## 5. Rollback
How to undo each step if something goes wrong.

## 6. Escalation
When to stop and ask for help. Who to contact.

## 7. Post-completion
What to document after the procedure. DEC or ADR to create. Memory to update.
```

---

## Active Playbooks

*(None yet — to be added as AEOS matures)*

---

## Planned Playbooks

| ID | Title | Priority |
|---|---|---|
| PB-001 | AEOS Release Procedure | High |
| PB-002 | Dependency Upgrade Procedure | High |
| PB-003 | Security Incident Response | High |
| PB-004 | Client Project Recovery — Stage 0 to Stage 1 | Medium |
| PB-005 | Constitutional Amendment Process | Medium |
| PB-006 | New Contributor Onboarding | Low |

---

## Numbering

Playbooks are numbered sequentially: `PB-001`, `PB-002`, etc. Numbers are never reused.
