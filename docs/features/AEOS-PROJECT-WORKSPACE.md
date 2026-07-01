# AEOS UI: Project Workspace

**Command:** `aeos ui project-workspace`
**Sprint:** MVP-UI-2
**Status:** SHIPPED

---

## Overview

`aeos ui project-workspace` generates a decision-ready static HTML document
from local MemoryRecords. It is designed to be shared with a CTO, DSI, or
founder before a deployment or governance decision — not as a developer
debugging view, but as a structured project briefing.

Unlike `aeos ui dashboard` (which shows a raw audit timeline), the workspace
presents derived narrative: an executive summary, a binary production
readiness verdict, human gates, and recommended next actions — all computed
from the same MemoryRecord files, with no additional network or AI calls.

---

## Usage

```sh
aeos ui project-workspace \
  --memory-dir /tmp/aeos-recovery-<project>/memory \
  --project <project-name> \
  --output /tmp/aeos-ui/<project>-workspace.html
```

### Options

| Flag | Required | Description |
|------|----------|-------------|
| `--memory-dir` | Yes | Path to directory containing local `*.json` MemoryRecord files |
| `--project` | Yes | Project name — used to filter records from the memory directory |
| `--output` / `-o` | Yes | Output HTML file path — created with parent directories if needed |
| `--overwrite` | No | Replace an existing output file (default: error if file exists) |

### Example output

```
Workspace:  /tmp/aeos-ui/ma-mairie-digitale-workspace.html
Project:    ma-mairie-digitale
Records:    6
Verdict:    NOT READY FOR PRODUCTION
Read-only — no files modified, no migration applied.
  read_only: true  ·  applied: false
```

---

## HTML Sections

The generated page contains 9 sections:

| # | Section | Content |
|---|---------|---------|
| 1 | Project Overview | Status, control level, generator, providers, last audit timestamp |
| 2 | Executive Summary | Plain-language status narrative derived from last record |
| 3 | Production Readiness | Binary verdict (READY / NOT READY) + list of blocking reasons |
| 4 | Recovery Progress | Before/after comparison table across all records with delta indicators |
| 5 | Completed Recovery Work | Measurable improvements with context (record count, date range) |
| 6 | Human Gates | Checklist of approvals required before proceeding |
| 7 | Risk Register | Categorical risk counts with severity labels and notes |
| 8 | Evidence | MemoryRecord metadata (first/last record IDs, read_only, applied flags) |
| 9 | Next Recommended Actions | Ordered list of concrete next steps |

---

## Derivation Logic

All content is computed from MemoryRecords — no hard-coded strings for
specific projects. Each section is derived as follows:

### Production Readiness

```
NOT READY if any of:
  - critical > 0
  - generated > 0   (SQL blocks not yet applied to staging)
  - manual > 0      (actions pending human review)
  - control_level == "weak"
```

### Executive Summary

Plain-language narrative selected by thresholds on `critical` and `important`
counts from the latest record, and the `important` delta from baseline.

### Human Gates

Derived from `providers` and `findings_summary`:
- `supabase` in providers → credential rotation + commune_id validation + RLS gate
- `critical > 0` → must-resolve gate
- `control_level` in `("weak", "partial")` → public data access decision gate
- `manual > 0` → manual review gate

### Next Actions

Derived from `generated`, `providers`, `critical`, `manual`, and
`control_level` on the last record. Falls back to "run next harden cycle" if
all counts are zero and control_level is strong.

---

## Design Constraints

| Constraint | Implementation |
|------------|---------------|
| Read-only | Never writes to the project directory or MemoryRecord files |
| No network | Zero HTTP calls — pure local file I/O |
| No AI | All derivation is deterministic Python logic |
| No secrets | MemoryRecords contain only counts and metadata — no `.env` values |
| No backend | One self-contained HTML file with embedded CSS |
| Static | No JavaScript, no WebSocket, no framework |
| Dark theme | `#0d1117` background, monospace font, 960px max-width |

---

## Data Source

- Input: `*.json` MemoryRecord files in `--memory-dir`, filtered by `--project`
- Loader: `aeos.memory.timeline.load_project_records`
- Records are sorted by `created_at` (oldest first)
- Baseline = first record; Current = last record
- Delta = `current - baseline` per metric (negative = improvement for counts)

---

## Read-Only Guarantee

The command:
- Does not read any `.env` files
- Does not modify any MemoryRecord files
- Does not contact any database or external service
- Does not apply any SQL migration
- Does not call any external AI model

Every generated page carries the footer:
```
read_only: true  ·  applied: false  ·  human validation required
```

---

## Relationship to `aeos ui dashboard`

| Feature | `aeos ui dashboard` | `aeos ui project-workspace` |
|---------|---------------------|----------------------------|
| Primary audience | Lead engineer / CTO debug view | CTO / DSI / founder decision briefing |
| Verdict | Not shown | Binary READY / NOT READY |
| Executive Summary | Not shown | Plain-language paragraph |
| Human Gates | Not shown | Explicit checklist |
| Timeline table | Shown (all records, with deltas) | Recovery Progress (summary only) |
| Risk categories | Not shown | Risk Register with notes |
| Synthesis trends | Shown | Not shown (aggregated into summary) |
| Width | 1200px (cockpit) | 960px (document) |

Both commands read the same MemoryRecords and can be run together.
