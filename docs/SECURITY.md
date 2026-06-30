# AEOS Security Policy

**Version:** 1.0.0
**Status:** Active
**Date:** 2026-06-30
**Governed by:** [CONSTITUTION.md](../CONSTITUTION.md) §6.1–6.2

---

## 1. Security Posture

AEOS is a security-first platform. Its security posture applies both to the software AEOS operates on (client projects) and to AEOS itself.

The six absolute safety requirements (CONSTITUTION §6.2, code-enforced):

1. **No secret exposure** — values never appear in any output, log, or transmitted context
2. **No unauthorized modification** — `read_only: true` default on all inspection commands
3. **No applied state without intent** — `applied: false` invariant on all read-only commands
4. **No silent frontier escalation** — `require_human_approval = true` stops and asks
5. **No destructive action without gate** — Level 4 required for any destructive operation
6. **No autonomous production change** — explicit human confirmation at Level 4

These are not policies. They are code-enforced invariants with tests. They cannot be overridden by agent behavior or configuration.

---

## 2. Secret Handling

### What AEOS never does

- Never reads `.env` file contents
- Never logs, displays, or transmits secret values
- Never stores credentials in `MemoryRecord`
- Never sends API keys, passwords, or tokens to any AI model
- Never writes secret values to any output file, report, or database

### What AEOS does instead

- Reports the *name* of a secret variable and its *presence* — never its value
- Reports `file:line` references — never `file:line:value`
- Strips sensitive data before any AI context is assembled
- Confirms secrets are absent from `MemoryRecord` before write

### Git history

AEOS scans Git history for secret variable names. If found:
- Reports the file, commit, and variable name
- Does not display the value
- Recommends rotation and (if necessary) `git filter-repo`

Credential rotation is irreversible. AEOS requires explicit human confirmation before any history rewrite instruction is generated.

---

## 3. Supply Chain Security

### Dependencies

AEOS Python dependencies are managed via `uv` and pinned in `pyproject.toml`. The dependency surface is intentionally minimal.

**Current runtime dependencies:**
- `typer` — CLI framework
- `rich` — terminal output
- `tomllib` / `tomli` — TOML parsing (stdlib in Python 3.11+)

No cloud SDKs. No authentication libraries. No database drivers. No telemetry.

### Audit cadence

- Dependency vulnerability scan: before each release
- `pip-audit` or equivalent: monthly or on any CVE notification
- No dependency upgrade without review and test passage

### What AEOS must not become

- No telemetry or analytics that transmits usage data
- No cloud service dependency in the CLI baseline
- No required external API calls in any `Level 0` or `Level 1` operation

---

## 4. Code Quality as Security

Static analysis and type checking are security controls, not only quality tools (CONSTITUTION §5.2):

```bash
uv run ruff check .       # linting — catches common error patterns
uv run mypy src           # strict type checking — prevents type confusion bugs
uv run pytest             # behavioral tests — verifies invariants hold
```

All three must pass before any merge. CI gate enforces this.

**Invariant tests are security tests.** The following are verified in the test suite:

- `read_only: true` on all inspection outputs
- `applied: false` on all inspection outputs
- No secret value in any output (test fixtures verify this structurally)
- `EvidenceReport` evidence status computed from declared indices only
- `MemoryRecord` has no credential fields

---

## 5. AI Security

### Local AI (default)

- Runs entirely on local infrastructure
- No data leaves the machine
- No authentication required for local Ollama endpoint
- Context assembled locally — no remote preprocessing

### Frontier AI (exception)

- Only called with explicit `provider="frontier"` or human-authorized `auto` mode
- `require_human_approval = true` — the router raises an error rather than silently escalating
- Context must be stripped of secrets and sensitive data before assembly
- All frontier calls must be logged

### What never goes to any AI model

- `.env` file contents
- Secret values (API keys, tokens, passwords, connection strings)
- Sensitive business data (PII, financial data, healthcare data)
- Database credentials
- Migration files with sensitive schema details (without anonymization)
- Client project data without explicit owner authorization

---

## 6. Development Security

### Branch protection

- `main` branch is protected
- No direct push to `main`
- All changes via PR with CI gate passing

### Secrets in the repository

- `.env` is in `.gitignore`
- No credentials in `aeos.toml` — only environment variable references
- `AEOS_FRONTIER_BASE_URL`, `AEOS_FRONTIER_API_KEY`, `AEOS_FRONTIER_MODEL` — environment only

### Commit hygiene

- Pre-commit check: ruff + mypy + pytest (or CI equivalent)
- No merge of a PR with failing tests
- No bypass of CI with `--no-verify`

---

## 7. Incident Response

### If a secret is accidentally committed

1. Rotate the credential immediately — before any other action
2. Assess whether the credential was exposed (public repo, CI logs)
3. Use `git filter-repo` to remove from history — only after rotation
4. Force-push the cleaned history with team notification
5. Document in `docs/DECISIONS.md` as a security incident

### If a dependency CVE is discovered

1. Assess severity and exploitability in the AEOS context
2. Pin to patched version in `pyproject.toml`
3. Run full test suite
4. Document the CVE reference and fix in `docs/DECISIONS.md`

### If an invariant is found to be violated

1. Write a failing test that reproduces the violation
2. Fix the code to make the test pass
3. Do not merge the fix without the test
4. Document the invariant violation in `docs/DECISIONS.md`

---

## 8. Security Review Cadence

| Activity | Frequency |
|---|---|
| Dependency vulnerability scan | Before each release, monthly |
| Invariant test coverage review | Each sprint |
| Secrets-in-history check (`aeos reclaim harden`) | On AEOS repo itself, quarterly |
| AI frontier usage audit | Monthly |
| Full security review | Annually or before any significant architecture change |

---

## See Also

- [CONSTITUTION.md](../CONSTITUTION.md) §6.1–6.2 — Quality and Safety Requirements
- [docs/SOVEREIGNTY.md](SOVEREIGNTY.md) — sovereignty posture
- [docs/AI-DEVELOPMENT-POLICY.md](AI-DEVELOPMENT-POLICY.md) — AI usage policy
- [ARCHITECTURE.md](../ARCHITECTURE.md) — system architecture and invariants
