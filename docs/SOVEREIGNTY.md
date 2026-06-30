# AEOS Sovereignty Posture

**Version:** 1.0.0
**Status:** Active
**Date:** 2026-06-30
**Governed by:** [CONSTITUTION.md](../CONSTITUTION.md) §1.1, §5.1

---

## 1. Principle

AEOS is a sovereign software continuity platform. It must embody the sovereignty principles it advocates.

A platform that recommends sovereignty to its users while depending on external cloud services, telemetry, or proprietary AI backends would be incoherent.

AEOS's own sovereignty posture is therefore a product constraint, not an operational preference.

---

## 2. Current Sovereignty Level

**AEOS self-assessment: Level 3 — Managed Open Source**

| Dimension | Status | Detail |
|---|---|---|
| Code | Sovereign | Fully owned, version-controlled, locally executable |
| Runtime | Sovereign | Python + uv — open, local, no cloud runtime |
| AI | Sovereign | Local AI (Ollama) by default; frontier by exception with human gate |
| Dependencies | Controlled | Minimal; no cloud SDKs; no telemetry |
| CI | Controlled | GitHub Actions — vendor dependency documented |
| Hosting | N/A | CLI tool — no hosted service at this stage |
| Data | Sovereign | MemoryRecords are local files; no cloud sync |
| Distribution | Controlled | PyPI distribution planned — vendor dependency |

The primary external vendor dependency is GitHub (repository hosting and CI). This is documented and accepted at the current stage. Exit option: Forgejo or GitLab self-hosted.

---

## 3. Dependency Posture

### Runtime dependencies (intentionally minimal)

| Package | Purpose | License | Sovereignty risk |
|---|---|---|---|
| `typer` | CLI framework | MIT | Low — replaceable |
| `rich` | Terminal output | MIT | Low — replaceable |
| `tomllib` | TOML parsing | Python stdlib 3.11+ | None |

No cloud SDKs. No authentication libraries. No database drivers. No telemetry packages.

### Development dependencies

| Package | Purpose | Sovereignty risk |
|---|---|---|
| `pytest` | Testing | Low |
| `ruff` | Linting | Low |
| `mypy` | Type checking | Low |
| `uv` | Package management | Low — Astral, MIT |

### Infrastructure dependencies

| Service | Purpose | Alternative | Exit cost |
|---|---|---|---|
| GitHub | Repository, CI | Forgejo, GitLab | Low — git history portable |
| Ollama | Local AI runtime | LM Studio, llama.cpp, vLLM | Low — configurable in aeos.toml |
| PyPI | Distribution | Self-hosted index, direct install | Low |

---

## 4. AI Sovereignty

AEOS's AI routing doctrine (see also [docs/AI-DEVELOPMENT-POLICY.md](AI-DEVELOPMENT-POLICY.md)):

```
Local AI by default.
Frontier AI by exception.
Human approval for sensitive operations.
```

**Local AI runtime:** Ollama at `http://localhost:11434`, model `llama3.2` by default. Configurable in `aeos.toml`.

**Frontier AI:** OpenAI-compatible endpoint. Configured via environment variables only:
- `AEOS_FRONTIER_BASE_URL`
- `AEOS_FRONTIER_API_KEY`
- `AEOS_FRONTIER_MODEL`

No frontier API keys in `aeos.toml`. No hardcoded endpoints. No default frontier model.

**Frontier AI is not required for any core AEOS function.** All Level 0–3 operations can be performed without frontier AI.

---

## 5. Exit Strategies

### Exit from GitHub

1. Export repository: `git clone --mirror`
2. Push to Forgejo or GitLab instance
3. Update remote URLs in `aeos.toml` references
4. Migrate CI pipelines to Woodpecker or GitLab CI (pipeline format is portable)

### Exit from Ollama

1. Update `[ai.local]` section in `aeos.toml` with new endpoint
2. Ollama, LM Studio, llama.cpp, and vLLM all expose OpenAI-compatible APIs
3. Model files are portable across runtimes

### Exit from PyPI distribution

1. Build: `uv build`
2. Distribute via direct install from Git: `pip install git+<repo-url>`
3. Or host a private PyPI index

---

## 6. What AEOS Must Not Introduce

The following would degrade AEOS's sovereignty posture and require a constitutional amendment to accept:

- **Telemetry or analytics** that transmits usage data to any external service
- **Cloud-mandatory features** that fail without a specific SaaS account
- **Proprietary AI dependencies** hardcoded into core functions
- **License changes** that restrict AEOS reuse, modification, or self-hosting
- **Required external authentication** for any local CLI operation

New dependencies that introduce any of the above must be rejected or routed through an RFC process with explicit sovereignty impact assessment.

---

## 7. Sovereignty Review

| Activity | Frequency |
|---|---|
| Dependency audit | Before each release |
| CI vendor review | Annually |
| AI routing audit | Quarterly |
| Full sovereignty self-assessment | Annually |

---

## See Also

- [CONSTITUTION.md](../CONSTITUTION.md) §1.1, §5.1 — Identity and Design Philosophy
- [docs/SECURITY.md](SECURITY.md) — security policy
- [docs/AI-DEVELOPMENT-POLICY.md](AI-DEVELOPMENT-POLICY.md) — AI usage policy
- [ARCHITECTURE.md](../ARCHITECTURE.md) — system architecture
- [docs/strategy/AEOS-PRODUCT-VISION.md](strategy/AEOS-PRODUCT-VISION.md) §7 — Sovereignty Levels
