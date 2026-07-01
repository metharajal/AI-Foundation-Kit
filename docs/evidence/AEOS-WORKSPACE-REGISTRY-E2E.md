# AEOS Workspace Registry — End-to-End Validation

**Date:** 2026-07-01
**Branch at validation:** main @ `7cda48c`
**Project tested:** ma-mairie-digitale
**Status:** PASSED

---

## Executive Summary

AEOS now operates as a fully self-contained local workspace system. Starting
from a single `aeos project register` call, a CTO or technical director can
generate a complete audit workspace — portfolio, dashboard, project workspace,
and full evidence pack — without specifying a registry path, without touching
any cloud service, and without running any backend.

This validation documents the first successful end-to-end run using the new
default AEOS registry at `~/.aeos/projects.json`.

---

## What Was Validated

| Capability | Result |
|-----------|--------|
| `aeos project register` without `--registry` | ✅ Writes to `~/.aeos/projects.json` |
| `aeos project list` without `--registry` | ✅ Reads from `~/.aeos/projects.json` |
| `aeos project show` without `--registry` | ✅ Reads from `~/.aeos/projects.json` |
| `aeos workspace demo` without `--registry` | ✅ Uses `~/.aeos/projects.json` automatically |
| Full workspace generated from scratch | ✅ 10 files, 1 project, 0 skipped |
| Git repo stayed clean after demo | ✅ `nothing to commit, working tree clean` |
| No network calls | ✅ Pure local file I/O |
| No secrets exposed | ✅ Only counts and metadata in MemoryRecords |
| No client project mutated | ✅ Read-only throughout |

---

## Commands Executed

```sh
# 1. Register the project — no --registry flag needed
uv run aeos project register \
  --name ma-mairie-digitale \
  --memory-dir /tmp/aeos-recovery-ma-mairie-digitale/memory \
  --evidence-dir /tmp/aeos-ui-demo/ma-mairie-digitale \
  --type recovered-project

# Output:
# Updated:     ma-mairie-digitale
# Type:         recovered-project
# Memory:       /tmp/aeos-recovery-ma-mairie-digitale/memory
# Evidence:     /tmp/aeos-ui-demo/ma-mairie-digitale
# Last seen:    2026-07-01T21:37:39Z
# Registry:     /Users/mohamadouamidoudiallo/.aeos/projects.json
# Total:        1 project(s) in registry
#   read_only: true · applied: false

# 2. List all registered projects
uv run aeos project list

# Output:
# Registry: /Users/mohamadouamidoudiallo/.aeos/projects.json  ·  1 project(s)  ·  local-only  ·  read-only
#
#   NAME                            TYPE                    LAST SEEN
#   ──────────────────────────────────────────────────────────────────────
#   ma-mairie-digitale              recovered-project       2026-07-01
#
#   read_only: true · applied: false

# 3. Show full project detail
uv run aeos project show --name ma-mairie-digitale

# Output:
# Project:      ma-mairie-digitale
# Type:         recovered-project
# Memory:       /tmp/aeos-recovery-ma-mairie-digitale/memory
# Evidence:     /tmp/aeos-ui-demo/ma-mairie-digitale
# Registered:   2026-07-01T21:07:39Z
# Last seen:    2026-07-01T21:37:39Z
# Local only:   true
# Read only:    true
# Registry:     /Users/mohamadouamidoudiallo/.aeos/projects.json
#   read_only: true · applied: false

# 4. Generate full workspace — no --registry flag needed
rm -rf /tmp/aeos-workspace-demo
uv run aeos workspace demo --output-dir /tmp/aeos-workspace-demo

# Output:
# Workspace:  /tmp/aeos-workspace-demo
# Registry:   /Users/mohamadouamidoudiallo/.aeos/projects.json
# Portfolio:  /tmp/aeos-workspace-demo/index.html
# Projects:   1 generated  ·  0 skipped
#   [OK]   ma-mairie-digitale  →  /tmp/aeos-workspace-demo/ma-mairie-digitale
# Read-only — no files modified, no migration applied.
#   read_only: true  ·  applied: false
```

---

## Registry Location

```
~/.aeos/projects.json   462B
```

Written automatically on first `aeos project register`. Never read by AEOS
outside of explicit CLI commands. Never synced. Never exposed. Local-only.

---

## Generated Workspace Tree

```
/tmp/aeos-workspace-demo/
  index.html                                ← portfolio (all projects)
  ma-mairie-digitale/
    dashboard.html                          ← audit cockpit
    project-workspace.html                  ← decision briefing
    evidence-pack/
      index.html                            ← evidence pack landing
      dashboard.html
      project-workspace.html
      recovery-summary.md
      risk-register.md
      human-gates.md
      next-actions.md
```

10 files generated. 0 skipped. All self-contained static HTML or Markdown.
No JavaScript. No backend. No CDN.

---

## What This Proves

1. **AEOS has a stable local identity.** The registry at `~/.aeos/projects.json`
   persists project metadata across sessions without any server or database.

2. **The full workspace chain works end-to-end.** From a single `register` call,
   a user can produce a complete CTO-ready audit workspace in one command.

3. **No configuration required.** None of the commands in this session required
   `--registry`. The default path is inferred automatically.

4. **The repo is not polluted.** `git status` showed `nothing to commit,
   working tree clean` throughout. The workspace lives in `/tmp`, not in the
   repo.

5. **Read-only guarantees held.** No client file was modified. No MemoryRecord
   was written. No migration was applied. No `.env` was read.

---

## Safety Guarantees

| Guarantee | Verification |
|-----------|-------------|
| No network | No HTTP client imported or called |
| No secrets | MemoryRecords contain only counts and status strings |
| No client mutation | Source project directories untouched |
| No migration applied | `applied: false` in all outputs |
| No `.env` read | Not referenced in any UI or workspace module |
| No AI call | All derivation is deterministic Python logic |
| Registry not modified during workspace generation | `load_registry` only — `save_registry` never called |
| Git repo clean | Verified with `git status` after full demo run |

---

## Current Limitations

| Limitation | Impact | Planned resolution |
|-----------|--------|-------------------|
| Single machine only | Registry not portable between workstations | By design (local-first) |
| `~/.aeos/projects.json` not backed up | Loss on disk wipe | User responsibility; future: `aeos registry export` |
| No `aeos project remove` command | Stale entries accumulate | Planned: MVP-CORE-4 |
| `workspace demo` errors if evidence-pack exists and no `--overwrite` | Friction on re-runs | Known; `--overwrite` flag available |
| `aeos ui portfolio` without `--output` has no default path | User must specify output | Acceptable for now |
| No `open` command integration | User must manually open HTML | Target: MVP-UX-1 |

---

## Decision: Next Phase

**MVP-UX-1 — Workspace Quickstart**

AEOS is functionally complete as a local audit workspace. The next gap is
the **first-use experience**: a new user (or a returning user on a fresh
machine) should be able to go from zero to open browser tab in under two
minutes without reading documentation.

### Target workflow

```sh
# Step 1 — register a project (one time)
aeos project register \
  --name <project> \
  --memory-dir <path>/memory \
  --type recovered-project

# Step 2 — generate the workspace
aeos workspace demo --output-dir ~/aeos-workspace

# Step 3 — open it
open ~/aeos-workspace/index.html
```

### What MVP-UX-1 would add

- A `quickstart` guide (Markdown) covering steps 1–3 end-to-end
- Possibly: `aeos workspace open` — calls `open` / `xdg-open` on the
  generated portfolio after `workspace demo` completes
- Possibly: `aeos workspace status` — shows what is registered and where
  the last workspace was generated

### Why this is the right next step

The technical foundation is solid. The remaining friction is entirely UX:
discoverability, first-run guidance, and the final "open in browser" step.
Solving this makes AEOS usable by a non-developer CTO without onboarding.
