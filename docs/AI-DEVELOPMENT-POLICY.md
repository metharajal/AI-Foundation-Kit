# AEOS AI Development Policy

**Version:** 1.0.0
**Status:** Active
**Date:** 2026-06-30
**Governed by:** [CONSTITUTION.md](../CONSTITUTION.md) §6.2, §5.1

---

## 1. Purpose

This document defines the policy governing AI usage during AEOS development itself — not the AI policy AEOS enforces for client projects.

AEOS must embody the AI doctrine it advocates. The rules below apply to every session where AI assistance (Claude Code, Claude, Cursor, Codex, or any other AI tool) is used to work on the AEOS codebase.

---

## 2. Core Doctrine

```
Local AI by default.
Frontier AI by exception.
Human approval for sensitive operations.
```

When using Claude Code or another frontier AI assistant directly on the AEOS codebase:

- The assistant operates as a **Level 0–3 tool** — it inspects, proposes, and prepares; it does not apply
- Every significant change is reviewed by a human before merge
- No secret values are shared with any AI assistant
- No client project data is shared with any AI assistant

---

## 3. What AI Assistants May Access

### Permitted

- AEOS source code (`src/aeos/`)
- AEOS documentation (`docs/`, `ARCHITECTURE.md`, `CONSTITUTION.md`, `MANIFESTO.md`)
- Test files (`tests/`)
- Configuration structure (`aeos.toml` — structure only, never values from environment)
- Git history for context on recent changes
- AEOS governance documents

### Prohibited

- `.env` file — never read, never shared
- Secret values of any kind (API keys, tokens, passwords)
- Client project code or data
- MemoryRecords from real client audits
- Any data that belongs to a third party

---

## 4. Session Startup Protocol

Before any AI assistant begins work on AEOS, it must read (in order):

1. `docs/strategy/AEOS-PRODUCT-VISION.md`
2. `docs/strategy/AEOS-PRODUCT-RAILS-AND-AGENTS.md`
3. `CONSTITUTION.md`
4. `docs/operations/AEOS-NEXT-ACTIONS.md`

Then:
- Summarize the current state
- Identify the active sprint or task
- Propose a plan before modifying files
- Never read `.env`
- Never display secrets
- Never touch client projects unless explicitly instructed
- Never apply fixes without a human gate

This startup protocol ensures the assistant has the context to make correct decisions without requiring constant re-briefing.

---

## 5. Code Generation Rules

### Always

- `from __future__ import annotations` in every new Python module
- `@dataclass` with `field(default_factory=list)` for mutable defaults
- Output types are read-only data structures
- New commands enforce `read_only: true` and `applied: false`
- Tests are written for new behavior before the behavior is considered complete
- Quality gate passes before any commit: `ruff check .` · `mypy src` · `pytest`

### Never

- Modify `MANIFESTO.md` — it is immutable
- Modify existing client audit records
- Add telemetry, analytics, or usage tracking
- Introduce a cloud-mandatory dependency without an RFC
- Write code that reads `.env` values
- Write code that logs or displays secret values
- Skip `--no-verify` or bypass CI

### Design constraints

- Do not add features beyond what the current task requires
- Do not introduce abstractions for hypothetical future requirements
- Do not add error handling for scenarios that cannot happen
- Three similar lines is better than a premature abstraction
- Comments only when the WHY is non-obvious

---

## 6. Review Gates

| Operation type | Review required | Gate level |
|---|---|---|
| Documentation change | Human review before merge | Level 2 |
| New Python module | Tests + quality gate + human review | Level 2–3 |
| New CLI command | Tests + quality gate + human review + PR | Level 3 |
| Existing command behavior change | Tests + quality gate + human review + PR | Level 3 |
| Invariant change (read_only, applied) | Constitutional review required | Level 4 |
| Dependency addition | Sovereignty impact assessment + RFC | Level 4 |
| CONSTITUTION.md amendment | RFC + ratification | Level 4 |

No change to AEOS safety invariants without constitutional review.

---

## 7. Frontier AI Usage in Development

Claude Code (Sonnet 4.6, Opus 4.8) is a frontier AI assistant. Using it on AEOS development is permitted under the following conditions:

- **Context is sanitized** — no `.env`, no secrets, no client data in the conversation
- **Human reviews all output** before merge
- **Tests are generated or updated** alongside any code change
- **Quality gates pass** before the change is considered complete
- **The human is in the loop** — no autonomous deployment, no autonomous PR merge

Claude Code acting on AEOS code is itself subject to the AEOS doctrine of "Agents propose. Humans decide."

---

## 8. Memory and Context Management

- AI assistant context may include AEOS code, documentation, and governance files
- AI assistant context must never include real credential values, client secrets, or personal data
- Memory files (`/Users/mohamadouamidoudiallo/.claude/projects/*/memory/`) may contain project context but must never contain secret values
- Session context is ephemeral — persistent decisions are recorded in `docs/DECISIONS.md`

---

## 9. Compliance Review

This policy is reviewed:
- When a new AI assistant is introduced to AEOS development
- When a significant version change in an AI assistant changes its capabilities
- Annually as part of the sovereignty review

Violations of this policy are documented in `docs/DECISIONS.md` as security incidents.

---

## See Also

- [CONSTITUTION.md](../CONSTITUTION.md) §6.2 — Safety Requirements
- [docs/SECURITY.md](SECURITY.md) — security policy
- [docs/SOVEREIGNTY.md](SOVEREIGNTY.md) — sovereignty posture
- [ARCHITECTURE.md](../ARCHITECTURE.md) §10 — AI Routing Architecture
- [docs/strategy/AEOS-PRODUCT-RAILS-AND-AGENTS.md](strategy/AEOS-PRODUCT-RAILS-AND-AGENTS.md) §5 — Local AI First doctrine
