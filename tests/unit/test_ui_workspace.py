"""Unit tests for aeos.ui.workspace and the `aeos ui project-workspace` CLI."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from aeos.cli import app
from aeos.memory.models import MemoryRecord
from aeos.memory.store import save_record
from aeos.ui.workspace import (
    ProductionReadiness,
    RecoveryProgress,
    WorkspaceData,
    _derive_executive_summary,
    _derive_human_gates,
    _derive_next_actions,
    _derive_production_readiness,
    load_workspace_data,
    render_workspace,
)


def _make_record(
    project_name: str = "test-proj",
    status: str = "ERROR",
    control_level: str = "weak",
    critical: int = 3,
    important: int = 72,
    manual: int = 15,
    generated: int = 25,
    generator: str | None = "lovable",
    providers: list[str] | None = None,
    read_only: bool = True,
    applied: bool = False,
    human_validated: bool = False,
    record_suffix: str = "aa001100",
) -> MemoryRecord:
    if providers is None:
        providers = ["supabase"]
    return MemoryRecord(
        record_id=f"{project_name}-20260630T110000-{record_suffix}",
        created_at="2026-06-30T11:00:00",
        project_path=f"/private/tmp/{project_name}",
        project_name=project_name,
        rail="reclaim",
        command="reclaim harden",
        status=status,
        generator=generator,
        providers=providers,
        control_level=control_level,
        read_only=read_only,
        applied=applied,
        findings_summary={
            "critical": critical,
            "important": important,
            "manual": manual,
            "generated": generated,
        },
        remediation_summary=None,
        strategic_options=["opt-a", "opt-b"],
        human_validated=human_validated,
        notes=None,
    )


def _write(tmp_path: Path, record: MemoryRecord) -> Path:
    return save_record(record, tmp_path)


runner = CliRunner()


# ---------------------------------------------------------------------------
# load_workspace_data
# ---------------------------------------------------------------------------


def test_load_raises_file_not_found(tmp_path: Path) -> None:
    missing = tmp_path / "no-such-dir"
    with pytest.raises(FileNotFoundError):
        load_workspace_data(missing, "proj")


def test_load_raises_value_error_no_records(tmp_path: Path) -> None:
    _write(tmp_path, _make_record(project_name="other-proj"))
    with pytest.raises(ValueError, match="No records found"):
        load_workspace_data(tmp_path, "test-proj")


def test_load_returns_workspace_data(tmp_path: Path) -> None:
    _write(tmp_path, _make_record())
    data = load_workspace_data(tmp_path, "test-proj")
    assert isinstance(data, WorkspaceData)
    assert data.project_name == "test-proj"
    assert len(data.records) == 1


def test_load_multi_record_populates_progress(tmp_path: Path) -> None:
    r1 = _make_record(important=72, generated=25, record_suffix="aa001")
    r2 = _make_record(important=59, generated=15, record_suffix="bb002")
    _write(tmp_path, r1)
    _write(tmp_path, r2)
    data = load_workspace_data(tmp_path, "test-proj")
    p = data.recovery_progress
    assert p.record_count == 2
    assert p.baseline["important"] == 72
    assert p.current["important"] == 59
    assert p.deltas["important"] == -13
    assert p.deltas["generated"] == -10


# ---------------------------------------------------------------------------
# _derive_production_readiness
# ---------------------------------------------------------------------------


def test_prod_readiness_not_ready_when_critical(tmp_path: Path) -> None:
    rec = _make_record(critical=3)
    pr = _derive_production_readiness(rec)
    assert not pr.ready
    assert "NOT READY" in pr.verdict
    assert any("critical" in r for r in pr.reasons)


def test_prod_readiness_not_ready_when_weak_control(tmp_path: Path) -> None:
    rec = _make_record(critical=0, generated=0, manual=0, control_level="weak")
    pr = _derive_production_readiness(rec)
    assert not pr.ready
    assert any("weak" in r for r in pr.reasons)


def test_prod_readiness_ready_when_all_clear() -> None:
    rec = _make_record(
        critical=0,
        important=0,
        manual=0,
        generated=0,
        control_level="strong",
    )
    pr = _derive_production_readiness(rec)
    assert pr.ready
    assert pr.verdict == "READY FOR PRODUCTION"
    assert pr.reasons == []


def test_prod_readiness_not_ready_when_generated_pending() -> None:
    rec = _make_record(critical=0, generated=5, manual=0, control_level="strong")
    pr = _derive_production_readiness(rec)
    assert not pr.ready
    assert any("SQL" in r for r in pr.reasons)


# ---------------------------------------------------------------------------
# _derive_executive_summary
# ---------------------------------------------------------------------------


def test_summary_mentions_critical_count() -> None:
    rec = _make_record(critical=3, important=59)
    p = RecoveryProgress(
        first_date="2026-06-30",
        last_date="2026-07-01",
        record_count=2,
        baseline={"critical": 3, "important": 72, "manual": 15, "generated": 25},
        current={"critical": 3, "important": 59, "manual": 15, "generated": 15},
        deltas={"critical": 0, "important": -13, "manual": 0, "generated": -10},
    )
    summary = _derive_executive_summary(rec, p)
    assert "3" in summary
    assert len(summary) > 20


def test_summary_no_critical_low_important() -> None:
    rec = _make_record(critical=0, important=5)
    p = RecoveryProgress(
        first_date="2026-06-30",
        last_date="2026-07-01",
        record_count=1,
        baseline={"critical": 0, "important": 5, "manual": 0, "generated": 0},
        current={"critical": 0, "important": 5, "manual": 0, "generated": 0},
        deltas={"critical": 0, "important": 0, "manual": 0, "generated": 0},
    )
    summary = _derive_executive_summary(rec, p)
    assert "controlled" in summary.lower()


# ---------------------------------------------------------------------------
# _derive_human_gates
# ---------------------------------------------------------------------------


def test_human_gates_supabase_provider() -> None:
    rec = _make_record(providers=["supabase"], critical=3, manual=5)
    gates = _derive_human_gates(rec)
    assert any("Supabase" in g for g in gates)
    assert any("RLS" in g for g in gates)
    assert len(gates) >= 3


def test_human_gates_no_supabase() -> None:
    rec = _make_record(
        providers=["firebase"], critical=0, manual=0, control_level="strong"
    )
    gates = _derive_human_gates(rec)
    assert not any("Supabase" in g for g in gates)


def test_human_gates_critical_adds_gate() -> None:
    rec = _make_record(providers=[], critical=2)
    gates = _derive_human_gates(rec)
    assert any("critical" in g.lower() for g in gates)


# ---------------------------------------------------------------------------
# _derive_next_actions
# ---------------------------------------------------------------------------


def test_next_actions_generated_sql_appears() -> None:
    rec = _make_record(generated=10, critical=0, manual=0)
    pr = ProductionReadiness(
        ready=False, verdict="NOT READY", reasons=["10 SQL blocks pending"]
    )
    actions = _derive_next_actions(rec, pr)
    assert any("SQL" in a for a in actions)


def test_next_actions_supabase_rotate_appears() -> None:
    rec = _make_record(providers=["supabase"])
    pr = ProductionReadiness(ready=False, verdict="NOT READY", reasons=[])
    actions = _derive_next_actions(rec, pr)
    assert any("Rotate" in a or "credentials" in a.lower() for a in actions)


def test_next_actions_fallback_when_all_clear() -> None:
    rec = _make_record(
        critical=0,
        important=0,
        manual=0,
        generated=0,
        providers=[],
        control_level="strong",
    )
    pr = ProductionReadiness(ready=True, verdict="READY", reasons=[])
    actions = _derive_next_actions(rec, pr)
    assert len(actions) == 1
    assert "harden" in actions[0].lower()


# ---------------------------------------------------------------------------
# render_workspace — HTML structure
# ---------------------------------------------------------------------------


def test_render_workspace_returns_html_string(tmp_path: Path) -> None:
    _write(tmp_path, _make_record())
    data = load_workspace_data(tmp_path, "test-proj")
    html = render_workspace(data)
    assert html.startswith("<!DOCTYPE html>")
    assert "</html>" in html


def test_render_workspace_has_all_section_headers(tmp_path: Path) -> None:
    _write(tmp_path, _make_record())
    data = load_workspace_data(tmp_path, "test-proj")
    html = render_workspace(data)
    for section in [
        "Project Overview",
        "Executive Summary",
        "Production Readiness",
        "Recovery Progress",
        "Completed Recovery Work",
        "Human Gates",
        "Risk Register",
        "Evidence",
        "Next Recommended Actions",
    ]:
        assert section in html, f"Missing section: {section}"


def test_render_workspace_shows_project_name(tmp_path: Path) -> None:
    _write(tmp_path, _make_record(project_name="my-proj"))
    data = load_workspace_data(tmp_path, "my-proj")
    html = render_workspace(data)
    assert "my-proj" in html


def test_render_workspace_verdict_not_ready(tmp_path: Path) -> None:
    _write(tmp_path, _make_record(critical=3))
    data = load_workspace_data(tmp_path, "test-proj")
    html = render_workspace(data)
    assert "NOT READY" in html


def test_render_workspace_verdict_ready(tmp_path: Path) -> None:
    rec = _make_record(
        critical=0, important=0, manual=0, generated=0, control_level="strong"
    )
    _write(tmp_path, rec)
    data = load_workspace_data(tmp_path, "test-proj")
    html = render_workspace(data)
    assert "READY FOR PRODUCTION" in html


def test_render_workspace_no_secrets(tmp_path: Path) -> None:
    _write(tmp_path, _make_record())
    data = load_workspace_data(tmp_path, "test-proj")
    html = render_workspace(data)
    # forbid raw secret VALUES — key names in advisory text are expected
    for bad in ["SECRET=", "eyJ", "password=", "SUPABASE_KEY="]:
        assert bad not in html


def test_render_workspace_read_only_badges(tmp_path: Path) -> None:
    _write(tmp_path, _make_record())
    data = load_workspace_data(tmp_path, "test-proj")
    html = render_workspace(data)
    assert "read_only: true" in html
    assert "applied: false" in html
    assert "human validation required" in html


def test_render_workspace_delta_table(tmp_path: Path) -> None:
    r1 = _make_record(important=72, generated=25, record_suffix="aa001")
    r2 = _make_record(important=59, generated=15, record_suffix="bb002")
    _write(tmp_path, r1)
    _write(tmp_path, r2)
    data = load_workspace_data(tmp_path, "test-proj")
    html = render_workspace(data)
    assert "72" in html
    assert "59" in html
    assert "25" in html
    assert "15" in html


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------


def test_cli_project_workspace_basic(tmp_path: Path) -> None:
    mem = tmp_path / "memory"
    mem.mkdir()
    _write(mem, _make_record())
    out = tmp_path / "workspace.html"
    result = runner.invoke(
        app,
        [
            "ui",
            "project-workspace",
            "--memory-dir",
            str(mem),
            "--project",
            "test-proj",
            "--output",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()
    assert "Workspace:" in result.output
    assert "read_only: true" in result.output


def test_cli_project_workspace_no_overwrite(tmp_path: Path) -> None:
    mem = tmp_path / "memory"
    mem.mkdir()
    _write(mem, _make_record())
    out = tmp_path / "ws.html"
    out.write_text("existing", encoding="utf-8")
    result = runner.invoke(
        app,
        [
            "ui",
            "project-workspace",
            "--memory-dir",
            str(mem),
            "--project",
            "test-proj",
            "--output",
            str(out),
        ],
    )
    assert result.exit_code == 1
    assert "already exists" in result.output


def test_cli_project_workspace_overwrite(tmp_path: Path) -> None:
    mem = tmp_path / "memory"
    mem.mkdir()
    _write(mem, _make_record())
    out = tmp_path / "ws.html"
    out.write_text("old", encoding="utf-8")
    result = runner.invoke(
        app,
        [
            "ui",
            "project-workspace",
            "--memory-dir",
            str(mem),
            "--project",
            "test-proj",
            "--output",
            str(out),
            "--overwrite",
        ],
    )
    assert result.exit_code == 0
    assert out.read_text(encoding="utf-8").startswith("<!DOCTYPE html>")


def test_cli_project_workspace_missing_memory_dir(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "ui",
            "project-workspace",
            "--memory-dir",
            str(tmp_path / "no-such"),
            "--project",
            "test-proj",
            "--output",
            str(tmp_path / "out.html"),
        ],
    )
    assert result.exit_code == 1


def test_cli_project_workspace_wrong_project(tmp_path: Path) -> None:
    mem = tmp_path / "memory"
    mem.mkdir()
    _write(mem, _make_record(project_name="real-proj"))
    result = runner.invoke(
        app,
        [
            "ui",
            "project-workspace",
            "--memory-dir",
            str(mem),
            "--project",
            "wrong-proj",
            "--output",
            str(tmp_path / "out.html"),
        ],
    )
    assert result.exit_code == 1
    assert "Error" in result.output


def test_cli_project_workspace_creates_parent_dirs(tmp_path: Path) -> None:
    mem = tmp_path / "memory"
    mem.mkdir()
    _write(mem, _make_record())
    out = tmp_path / "nested" / "deep" / "ws.html"
    result = runner.invoke(
        app,
        [
            "ui",
            "project-workspace",
            "--memory-dir",
            str(mem),
            "--project",
            "test-proj",
            "--output",
            str(out),
        ],
    )
    assert result.exit_code == 0
    assert out.exists()


def test_cli_project_workspace_output_is_immutable(tmp_path: Path) -> None:
    """The CLI does not modify existing MemoryRecord files."""
    mem = tmp_path / "memory"
    mem.mkdir()
    saved = _write(mem, _make_record())
    mtime_before = saved.stat().st_mtime
    runner.invoke(
        app,
        [
            "ui",
            "project-workspace",
            "--memory-dir",
            str(mem),
            "--project",
            "test-proj",
            "--output",
            str(tmp_path / "ws.html"),
        ],
    )
    assert saved.stat().st_mtime == mtime_before


def test_cli_project_workspace_verdict_in_output(tmp_path: Path) -> None:
    mem = tmp_path / "memory"
    mem.mkdir()
    _write(mem, _make_record(critical=3))
    out = tmp_path / "ws.html"
    result = runner.invoke(
        app,
        [
            "ui",
            "project-workspace",
            "--memory-dir",
            str(mem),
            "--project",
            "test-proj",
            "--output",
            str(out),
        ],
    )
    assert result.exit_code == 0
    assert "NOT READY" in result.output
