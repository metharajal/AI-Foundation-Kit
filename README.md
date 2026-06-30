# AEOS — Sovereign Software Continuity Platform

> **Lovable is a use case. Reclaim is a rail. AEOS is the full engineering operating system.**

AEOS is a **sovereign software continuity platform** — a local-first, open-source-first, AI-local-first engineering system for creating, reclaiming, modernizing, migrating, evolving, and operating digital products with AI.

It turns an idea, a prototype, an AI-generated project, a monolith, or a legacy system into software that is mastered, auditable, portable, secure, and sovereign.

Governed by [MANIFESTO.md](MANIFESTO.md) and [CONSTITUTION.md](CONSTITUTION.md).

---

## Nine Product Rails

| Rail | Capability | Status |
|---|---|---|
| **Build** | Continue · Govern | **Production** |
| **Reclaim** | Discover · Assess · Recover | **Production** |
| **Modernize** | Discover · Assess · Transform | Planned |
| **Migrate** | Transform · Recover | Planned |
| **Operate** | Operate · Assess | Planned |
| **Security** | Assess · Govern | **Production** |
| **Sovereignty** | Assess · Govern | **Production** |
| **Agents** | All | In progress |
| **Memory** | Learn | **Production** |

---

## Current Commands (Production-Ready)

```bash
# Reclaim — read-only audit and recovery planning
aeos reclaim inspect --path <project>
aeos reclaim harden --path <project> [--output <file>]
aeos reclaim recovery plan --path <project> [--json] [--output <file>]
aeos reclaim evidence report --stage <stage_id> [--confirmed <n>...] [--json]
aeos reclaim evidence summary [--json]

# Supabase-specific audit chain
aeos supabase check --path <project>
aeos supabase rls inspect --path <project>
aeos supabase rls harden --path <project> [--output <file>]

# Security and sovereignty
aeos security check --path <project>
aeos sovereignty check --path <project>

# Build — architecture planning and scaffolding
aeos build plan --name <name> --type <type> --stack <stack> [--json]
aeos build scaffold --name <name> --type <type> --stack <stack> --output <dir>

# Memory — local audit knowledge base
aeos memory list --memory-dir <dir> [--json]
aeos memory show --memory-dir <dir> --record <id> [--json]
aeos memory compare --memory-dir <dir> --left <id> --right <id> [--json]
aeos memory timeline --memory-dir <dir> --project <name> [--json]
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

**Governance:**
- [`MANIFESTO.md`](MANIFESTO.md) — supreme document, immutable
- [`CONSTITUTION.md`](CONSTITUTION.md) — identity, invariants, and governance (v1.0.0)
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — system architecture, engines, interfaces, levels
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — decision log
- [`docs/SECURITY.md`](docs/SECURITY.md) — security policy
- [`docs/SOVEREIGNTY.md`](docs/SOVEREIGNTY.md) — sovereignty posture
- [`docs/AI-DEVELOPMENT-POLICY.md`](docs/AI-DEVELOPMENT-POLICY.md) — AI usage policy

**Strategy:**
- [`docs/strategy/AEOS-PRODUCT-RAILS-AND-AGENTS.md`](docs/strategy/AEOS-PRODUCT-RAILS-AND-AGENTS.md) — nine product rails, agent matrix, governance rules
- [`docs/strategy/AEOS-PRODUCT-VISION.md`](docs/strategy/AEOS-PRODUCT-VISION.md) — full strategic vision, use cases, target users, positioning

**Features:**
- [`docs/features/AEOS-RECLAIM-HARDEN.md`](docs/features/AEOS-RECLAIM-HARDEN.md) — Reclaim Rail harden command
- [`docs/features/AEOS-RECLAIM-RECOVERY.md`](docs/features/AEOS-RECLAIM-RECOVERY.md) — Recovery plan command
- [`docs/features/AEOS-MEMORY-LAYER.md`](docs/features/AEOS-MEMORY-LAYER.md) — Memory Layer
- [`docs/features/AEOS-BUILD-RAIL.md`](docs/features/AEOS-BUILD-RAIL.md) — Build Rail
- [`docs/features/AEOS-SUPABASE-RLS-HARDENING.md`](docs/features/AEOS-SUPABASE-RLS-HARDENING.md) — RLS hardening chain
