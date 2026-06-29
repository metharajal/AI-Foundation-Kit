# AEOS — AI Engineering Operating System

> **Lovable is a use case. Reclaim is a rail. AEOS is the full engineering operating system.**

AEOS is a local-first, open-source-first, AI-local-first engineering system for creating, reclaiming, modernizing, migrating, evolving, and operating digital products with AI.

It turns an idea, a prototype, an AI-generated project, a monolith, or a legacy system into software that is mastered, auditable, portable, secure, and sovereign.

---

## Nine Product Rails

| Rail | Purpose | Status |
|---|---|---|
| **Build** | Start new projects with sovereignty and engineering discipline from commit 1 | Planned |
| **Reclaim** | Audit, harden, and recover control of AI-generated or no-code projects | **Production** |
| **Modernize** | Understand and progressively transform legacy monolithic applications | Planned |
| **Migrate** | Move from one architecture to another — controlled, tested, reversible | Planned |
| **Operate** | Continuous audit, security, optimization, and documentation | Planned |
| **Security** | Cross-cutting security verification — always read-only, always non-destructive | **Production** |
| **Sovereignty** | Detect, measure, and reduce external platform dependency | **Production** |
| **Agents** | Cross-cutting task execution with specialized AI agents | In progress |
| **Memory** | Local, controlled knowledge accumulation — validated by humans | Planned |

---

## Current Commands (Production-Ready)

```bash
# Full cross-domain audit — read-only
aeos reclaim inspect --path <project>
aeos reclaim harden --path <project>
aeos reclaim harden --path <project> --output <file>

# Supabase-specific audit chain
aeos supabase check --path <project>
aeos supabase rls inspect --path <project>
aeos supabase rls harden --path <project>
aeos supabase rls harden --path <project> --output <file>

# Security and sovereignty
aeos security check --path <project>
aeos sovereignty check --path <project>
```

All audit commands are **read-only**. No client file is modified. No database connection is opened. No secret value is read or displayed.

---

## Core Architecture

```
AEOS Core         — guarantees
AEOS Agents       — reason
AEOS Memory       — learns
Humans            — validate
```

**Local AI by default. Frontier AI by exception. Human approval for sensitive operations.**

---

## Security Invariants

These are code-enforced on every audit command. They cannot be overridden by any flag:

| Invariant | Value |
|---|---|
| `read_only` | `true` — no client file is ever written |
| `applied` | `false` — no SQL migration is applied |
| No `.env` read | Variable names only; values are never read or displayed |
| No secret display | Evidence references `file:line`, never `file:line:value` |
| No database connection | No credentials needed or used |

---

## Documentation

- [`docs/strategy/AEOS-PRODUCT-RAILS-AND-AGENTS.md`](docs/strategy/AEOS-PRODUCT-RAILS-AND-AGENTS.md) — nine product rails, agent matrix, governance rules, what AEOS must not become
- [`docs/strategy/AEOS-PRODUCT-VISION.md`](docs/strategy/AEOS-PRODUCT-VISION.md) — full strategic vision, use cases, target users, positioning
- [`docs/features/AEOS-RECLAIM-HARDEN.md`](docs/features/AEOS-RECLAIM-HARDEN.md) — Reclaim Rail harden command documentation
- [`docs/features/AEOS-SUPABASE-RLS-HARDENING.md`](docs/features/AEOS-SUPABASE-RLS-HARDENING.md) — RLS hardening chain documentation
