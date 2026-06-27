"""
Unit tests for the Supabase RLS Plan Advisor (Sprint 2U).
"""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from aeos.cli import app
from aeos.providers.supabase.rls import run_rls_plan
from aeos.providers.supabase.rls.inspector import RLSFinding
from aeos.providers.supabase.rls.planner import (
    RLSPlanAction,
    _build_summary,
    _extract_policy_name,
    _finding_priority,
    _finding_to_action,
)

runner = CliRunner()

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "supabase_rls"


# ---------------------------------------------------------------------------
# Helpers for building test findings
# ---------------------------------------------------------------------------


def _make_finding(
    rule: str,
    severity: str,
    table: str = "test_table",
    message: str = "",
    recommendation: str = "Fix it.",
    source_file: str = "migrations/001.sql:10",
) -> RLSFinding:
    if not message:
        message = f"Policy 'test_policy' on '{table}' has issue."
    return RLSFinding(
        severity=severity,
        table=table,
        rule=rule,
        message=message,
        recommendation=recommendation,
        source_file=source_file,
    )


# ---------------------------------------------------------------------------
# TestExtractPolicyName
# ---------------------------------------------------------------------------


class TestExtractPolicyName:
    def test_extracts_name(self) -> None:
        msg = "Policy 'My Policy' on 'table' has an issue."
        assert _extract_policy_name(msg) == "My Policy"

    def test_returns_empty_when_absent(self) -> None:
        assert _extract_policy_name("Table 'foo' has no RLS enabled.") == ""

    def test_extracts_first_occurrence(self) -> None:
        msg = "Policy 'first' on 'table': see Policy 'second'."
        assert _extract_policy_name(msg) == "first"


# ---------------------------------------------------------------------------
# TestFindingPriority
# ---------------------------------------------------------------------------


class TestFindingPriority:
    def test_no_rls_is_critical(self) -> None:
        f = _make_finding("NO_RLS", "ERROR")
        assert _finding_priority(f) == "CRITICAL"

    def test_sensitive_open_select_is_critical(self) -> None:
        f = _make_finding("SENSITIVE_TABLE_OPEN_SELECT", "ERROR")
        assert _finding_priority(f) == "CRITICAL"

    def test_select_too_permissive_error_is_critical(self) -> None:
        f = _make_finding("SELECT_TOO_PERMISSIVE", "ERROR")
        assert _finding_priority(f) == "CRITICAL"

    def test_select_too_permissive_warning_is_medium(self) -> None:
        f = _make_finding("SELECT_TOO_PERMISSIVE", "WARNING")
        assert _finding_priority(f) == "MEDIUM"

    def test_no_policies_is_high(self) -> None:
        f = _make_finding("NO_POLICIES", "ERROR")
        assert _finding_priority(f) == "HIGH"

    def test_insert_no_with_check_is_high(self) -> None:
        f = _make_finding("INSERT_NO_WITH_CHECK", "WARNING")
        assert _finding_priority(f) == "HIGH"

    def test_update_no_with_check_is_high(self) -> None:
        f = _make_finding("UPDATE_NO_WITH_CHECK", "WARNING")
        assert _finding_priority(f) == "HIGH"

    def test_missing_tenant_scope_is_high(self) -> None:
        f = _make_finding("MISSING_TENANT_SCOPE", "WARNING")
        assert _finding_priority(f) == "HIGH"

    def test_no_delete_policy_is_medium(self) -> None:
        f = _make_finding("NO_DELETE_POLICY", "WARNING")
        assert _finding_priority(f) == "MEDIUM"

    def test_auth_role_authenticated_is_medium(self) -> None:
        f = _make_finding("AUTH_ROLE_AUTHENTICATED", "WARNING")
        assert _finding_priority(f) == "MEDIUM"

    def test_unknown_rule_is_low(self) -> None:
        f = _make_finding("UNKNOWN_RULE", "WARNING")
        assert _finding_priority(f) == "LOW"


# ---------------------------------------------------------------------------
# TestFindingToAction
# ---------------------------------------------------------------------------


class TestFindingToAction:
    def test_fields_populated(self) -> None:
        f = _make_finding(
            rule="INSERT_NO_WITH_CHECK",
            severity="WARNING",
            table="profiles",
            message=(
                "Policy 'insert_own' on 'profiles' covers INSERT but has no WITH CHECK."
            ),
            recommendation="Add WITH CHECK.",
            source_file="migrations/001.sql:42",
        )
        action = _finding_to_action(f, order=1)
        assert action.order == 1
        assert action.priority == "HIGH"
        assert action.table == "profiles"
        assert action.policy == "insert_own"
        assert action.risk_type == "INSERT_NO_WITH_CHECK"
        assert action.severity == "WARNING"
        assert action.problem == f.message
        assert action.fix == "Add WITH CHECK."
        assert action.functional_impact != ""
        assert action.recommended_test != ""
        assert action.source_file == "migrations/001.sql:42"

    def test_table_level_finding_has_empty_policy(self) -> None:
        f = _make_finding(
            rule="NO_DELETE_POLICY",
            severity="WARNING",
            table="forum_posts",
            message="Table 'forum_posts' has no DELETE policy.",
        )
        action = _finding_to_action(f, order=1)
        assert action.policy == ""

    def test_order_propagated(self) -> None:
        f = _make_finding("NO_RLS", "ERROR")
        action = _finding_to_action(f, order=7)
        assert action.order == 7

    def test_critical_escalation_select_error(self) -> None:
        f = _make_finding("SELECT_TOO_PERMISSIVE", "ERROR", table="personnel")
        action = _finding_to_action(f, order=1)
        assert action.priority == "CRITICAL"

    def test_medium_for_select_warning(self) -> None:
        f = _make_finding("SELECT_TOO_PERMISSIVE", "WARNING", table="associations")
        action = _finding_to_action(f, order=1)
        assert action.priority == "MEDIUM"

    def test_no_rls_impact_mentions_isolation(self) -> None:
        f = _make_finding("NO_RLS", "ERROR")
        action = _finding_to_action(f, order=1)
        assert "isolation" in action.functional_impact.lower()

    def test_update_no_with_check_test_mentions_user_id(self) -> None:
        f = _make_finding("UPDATE_NO_WITH_CHECK", "WARNING")
        action = _finding_to_action(f, order=1)
        assert "user_id" in action.recommended_test

    def test_missing_tenant_scope_test_mentions_commune_id(self) -> None:
        f = _make_finding("MISSING_TENANT_SCOPE", "WARNING")
        action = _finding_to_action(f, order=1)
        assert "commune_id" in action.recommended_test


# ---------------------------------------------------------------------------
# TestBuildSummary
# ---------------------------------------------------------------------------


class TestBuildSummary:
    def _make_action(self, priority: str, table: str) -> RLSPlanAction:
        return RLSPlanAction(
            order=1,
            priority=priority,
            table=table,
            policy="",
            risk_type="TEST",
            severity="WARNING",
            problem="",
            fix="",
            functional_impact="",
            recommended_test="",
            source_file="",
        )

    def test_counts_by_priority(self) -> None:
        actions = [
            self._make_action("CRITICAL", "t1"),
            self._make_action("HIGH", "t2"),
            self._make_action("HIGH", "t3"),
            self._make_action("MEDIUM", "t4"),
        ]
        summary = _build_summary(actions)
        assert summary.by_priority["CRITICAL"] == 1
        assert summary.by_priority["HIGH"] == 2
        assert summary.by_priority["MEDIUM"] == 1
        assert summary.by_priority["LOW"] == 0

    def test_total_actions(self) -> None:
        actions = [self._make_action("HIGH", "t") for _ in range(5)]
        summary = _build_summary(actions)
        assert summary.total_actions == 5

    def test_riskiest_tables_sorted(self) -> None:
        actions = [
            self._make_action("HIGH", "alpha"),
            self._make_action("HIGH", "alpha"),
            self._make_action("HIGH", "alpha"),
            self._make_action("MEDIUM", "beta"),
            self._make_action("MEDIUM", "beta"),
            self._make_action("LOW", "gamma"),
        ]
        summary = _build_summary(actions)
        assert summary.riskiest_tables[0] == "alpha"
        assert "beta" in summary.riskiest_tables

    def test_riskiest_tables_capped_at_five(self) -> None:
        actions = [self._make_action("HIGH", f"t{i}") for i in range(10)]
        summary = _build_summary(actions)
        assert len(summary.riskiest_tables) == 5

    def test_application_order_skips_empty(self) -> None:
        actions = [
            self._make_action("CRITICAL", "t1"),
            self._make_action("MEDIUM", "t2"),
        ]
        summary = _build_summary(actions)
        assert summary.application_order == ["CRITICAL", "MEDIUM"]
        assert "HIGH" not in summary.application_order
        assert "LOW" not in summary.application_order

    def test_application_order_canonical_sequence(self) -> None:
        actions = [
            self._make_action("LOW", "t1"),
            self._make_action("CRITICAL", "t2"),
            self._make_action("HIGH", "t3"),
            self._make_action("MEDIUM", "t4"),
        ]
        summary = _build_summary(actions)
        assert summary.application_order == ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

    def test_empty_actions(self) -> None:
        summary = _build_summary([])
        assert summary.total_actions == 0
        assert summary.riskiest_tables == []
        assert summary.application_order == []


# ---------------------------------------------------------------------------
# TestRunRLSPlan — fixture-based
# ---------------------------------------------------------------------------


class TestRunRLSPlanNoMigrations:
    def test_no_migrations_returns_ok(self, tmp_path: Path) -> None:
        result = run_rls_plan(tmp_path)
        assert result.status == "OK"
        assert result.migrations_scanned == 0
        assert result.actions == []
        assert result.read_only is True

    def test_no_migrations_summary_zeros(self, tmp_path: Path) -> None:
        result = run_rls_plan(tmp_path)
        assert result.summary.total_actions == 0
        assert all(v == 0 for v in result.summary.by_priority.values())

    def test_path_is_absolute(self, tmp_path: Path) -> None:
        result = run_rls_plan(tmp_path)
        assert result.path.is_absolute()

    def test_read_only_flag_always_true(self, tmp_path: Path) -> None:
        result = run_rls_plan(tmp_path)
        assert result.read_only is True


class TestRunRLSPlanFixture:
    def test_returns_actions(self) -> None:
        result = run_rls_plan(FIXTURE_DIR)
        assert len(result.actions) > 0

    def test_actions_ordered_by_priority(self) -> None:
        result = run_rls_plan(FIXTURE_DIR)
        order_map = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        priorities = [order_map[a.priority] for a in result.actions]
        assert priorities == sorted(priorities)

    def test_action_order_numbers_sequential(self) -> None:
        result = run_rls_plan(FIXTURE_DIR)
        orders = [a.order for a in result.actions]
        assert orders == list(range(1, len(orders) + 1))

    def test_critical_before_high(self) -> None:
        result = run_rls_plan(FIXTURE_DIR)
        priorities = [a.priority for a in result.actions]
        if "CRITICAL" in priorities and "HIGH" in priorities:
            first_critical = priorities.index("CRITICAL")
            first_high = priorities.index("HIGH")
            assert first_critical < first_high

    def test_sensitive_table_select_is_critical(self) -> None:
        result = run_rls_plan(FIXTURE_DIR)
        critical_rules = {
            a.risk_type for a in result.actions if a.priority == "CRITICAL"
        }
        assert "SELECT_TOO_PERMISSIVE" in critical_rules or (
            "SENSITIVE_TABLE_OPEN_SELECT" in critical_rules
        )

    def test_insert_no_with_check_is_high(self) -> None:
        result = run_rls_plan(FIXTURE_DIR)
        high_rules = {a.risk_type for a in result.actions if a.priority == "HIGH"}
        assert (
            "INSERT_NO_WITH_CHECK" in high_rules or "UPDATE_NO_WITH_CHECK" in high_rules
        )

    def test_no_delete_policy_is_medium(self) -> None:
        result = run_rls_plan(FIXTURE_DIR)
        medium_rules = {a.risk_type for a in result.actions if a.priority == "MEDIUM"}
        assert "NO_DELETE_POLICY" in medium_rules

    def test_all_actions_have_impact(self) -> None:
        result = run_rls_plan(FIXTURE_DIR)
        assert all(a.functional_impact for a in result.actions)

    def test_all_actions_have_test(self) -> None:
        result = run_rls_plan(FIXTURE_DIR)
        assert all(a.recommended_test for a in result.actions)

    def test_all_actions_have_fix(self) -> None:
        result = run_rls_plan(FIXTURE_DIR)
        assert all(a.fix for a in result.actions)

    def test_status_matches_inspect(self) -> None:
        from aeos.providers.supabase.rls import run_rls_inspect

        plan = run_rls_plan(FIXTURE_DIR)
        inspect = run_rls_inspect(FIXTURE_DIR)
        assert plan.status == inspect.status

    def test_recommendations_non_empty(self) -> None:
        result = run_rls_plan(FIXTURE_DIR)
        assert len(result.recommendations) > 0

    def test_stable_ordering(self) -> None:
        result1 = run_rls_plan(FIXTURE_DIR)
        result2 = run_rls_plan(FIXTURE_DIR)
        orders1 = [(a.priority, a.table, a.risk_type) for a in result1.actions]
        orders2 = [(a.priority, a.table, a.risk_type) for a in result2.actions]
        assert orders1 == orders2

    def test_read_only_flag(self) -> None:
        result = run_rls_plan(FIXTURE_DIR)
        assert result.read_only is True


# ---------------------------------------------------------------------------
# TestCLISupabaseRLSPlan — text output
# ---------------------------------------------------------------------------


class TestCLIPlanTextOutput:
    def test_exits_nonzero_on_error(self) -> None:
        r = runner.invoke(app, ["supabase", "rls", "plan", "--path", str(FIXTURE_DIR)])
        assert r.exit_code == 1

    def test_shows_header(self) -> None:
        r = runner.invoke(app, ["supabase", "rls", "plan", "--path", str(FIXTURE_DIR)])
        assert "Supabase RLS Plan Advisor" in r.output

    def test_shows_status(self) -> None:
        r = runner.invoke(app, ["supabase", "rls", "plan", "--path", str(FIXTURE_DIR)])
        assert "Status:" in r.output

    def test_shows_executive_summary(self) -> None:
        r = runner.invoke(app, ["supabase", "rls", "plan", "--path", str(FIXTURE_DIR)])
        assert "Executive Summary" in r.output

    def test_shows_critical_section(self) -> None:
        r = runner.invoke(app, ["supabase", "rls", "plan", "--path", str(FIXTURE_DIR)])
        assert "CRITICAL" in r.output

    def test_shows_fix_order(self) -> None:
        r = runner.invoke(app, ["supabase", "rls", "plan", "--path", str(FIXTURE_DIR)])
        assert "Fix order" in r.output

    def test_shows_recommendations(self) -> None:
        r = runner.invoke(app, ["supabase", "rls", "plan", "--path", str(FIXTURE_DIR)])
        assert "Recommendations" in r.output

    def test_shows_read_only_notice(self) -> None:
        r = runner.invoke(app, ["supabase", "rls", "plan", "--path", str(FIXTURE_DIR)])
        assert "Read-only audit" in r.output

    def test_no_migrations_exits_zero(self, tmp_path: Path) -> None:
        r = runner.invoke(app, ["supabase", "rls", "plan", "--path", str(tmp_path)])
        assert r.exit_code == 0

    def test_nonexistent_path_exits_nonzero(self) -> None:
        r = runner.invoke(
            app, ["supabase", "rls", "plan", "--path", "/nonexistent/path/xyz"]
        )
        assert r.exit_code != 0

    def test_shows_problem_and_fix(self) -> None:
        r = runner.invoke(app, ["supabase", "rls", "plan", "--path", str(FIXTURE_DIR)])
        assert "Problem:" in r.output
        assert "Fix:" in r.output

    def test_shows_impact_and_test(self) -> None:
        r = runner.invoke(app, ["supabase", "rls", "plan", "--path", str(FIXTURE_DIR)])
        assert "Impact:" in r.output
        assert "Test:" in r.output


# ---------------------------------------------------------------------------
# TestCLIPlanJSONOutput
# ---------------------------------------------------------------------------


class TestCLIPlanJSONOutput:
    def _get_json(self, path: str | None = None) -> dict:  # type: ignore[type-arg]
        target = path or str(FIXTURE_DIR)
        r = runner.invoke(app, ["supabase", "rls", "plan", "--path", target, "--json"])
        return json.loads(r.output)

    def test_valid_json(self) -> None:
        r = runner.invoke(
            app, ["supabase", "rls", "plan", "--path", str(FIXTURE_DIR), "--json"]
        )
        data = json.loads(r.output)
        assert isinstance(data, dict)

    def test_read_only_true(self) -> None:
        data = self._get_json()
        assert data["read_only"] is True

    def test_status_field(self) -> None:
        data = self._get_json()
        assert data["status"] in ("OK", "WARNING", "ERROR")

    def test_summary_present(self) -> None:
        data = self._get_json()
        assert "summary" in data
        s = data["summary"]
        assert "total_actions" in s
        assert "by_priority" in s
        assert "riskiest_tables" in s
        assert "application_order" in s

    def test_by_priority_has_all_keys(self) -> None:
        data = self._get_json()
        bp = data["summary"]["by_priority"]
        assert set(bp.keys()) == {"CRITICAL", "HIGH", "MEDIUM", "LOW"}

    def test_actions_list_present(self) -> None:
        data = self._get_json()
        assert "actions" in data
        assert isinstance(data["actions"], list)

    def test_actions_have_required_fields(self) -> None:
        data = self._get_json()
        required = {
            "order",
            "priority",
            "table",
            "policy",
            "risk_type",
            "severity",
            "problem",
            "fix",
            "functional_impact",
            "recommended_test",
            "source_file",
        }
        for action in data["actions"]:
            assert required <= set(action.keys()), f"Missing fields in: {action}"

    def test_priority_values_valid(self) -> None:
        data = self._get_json()
        valid = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        for action in data["actions"]:
            assert action["priority"] in valid

    def test_recommendations_list(self) -> None:
        data = self._get_json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    def test_total_actions_matches_actions_list(self) -> None:
        data = self._get_json()
        assert data["summary"]["total_actions"] == len(data["actions"])

    def test_no_migrations_json_structure(self, tmp_path: Path) -> None:
        r = runner.invoke(
            app, ["supabase", "rls", "plan", "--path", str(tmp_path), "--json"]
        )
        data = json.loads(r.output)
        assert data["summary"]["total_actions"] == 0
        assert data["actions"] == []
        assert data["read_only"] is True

    def test_application_order_is_subset_of_priorities(self) -> None:
        data = self._get_json()
        valid = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        for p in data["summary"]["application_order"]:
            assert p in valid


# ---------------------------------------------------------------------------
# TestAntiLeakage
# ---------------------------------------------------------------------------


class TestAntiLeakage:
    def test_no_env_file_read(self) -> None:
        env_file = FIXTURE_DIR / ".env"
        env_file.write_text("SECRET_KEY=should_not_appear\n")
        try:
            r = runner.invoke(
                app, ["supabase", "rls", "plan", "--path", str(FIXTURE_DIR)]
            )
            assert "should_not_appear" not in r.output
        finally:
            env_file.unlink(missing_ok=True)

    def test_no_env_json_leak(self) -> None:
        env_file = FIXTURE_DIR / ".env"
        env_file.write_text("SECRET_KEY=json_leak_test\n")
        try:
            r = runner.invoke(
                app,
                ["supabase", "rls", "plan", "--path", str(FIXTURE_DIR), "--json"],
            )
            assert "json_leak_test" not in r.output
        finally:
            env_file.unlink(missing_ok=True)

    def test_does_not_modify_fixture(self) -> None:
        def fingerprint(d: Path) -> dict[str, int]:
            return {
                str(p.relative_to(d)): p.stat().st_size
                for p in sorted(d.rglob("*"))
                if p.is_file()
            }

        before = fingerprint(FIXTURE_DIR)
        runner.invoke(app, ["supabase", "rls", "plan", "--path", str(FIXTURE_DIR)])
        after = fingerprint(FIXTURE_DIR)
        assert before == after


# ---------------------------------------------------------------------------
# TestPlanVsInspectConsistency
# ---------------------------------------------------------------------------


class TestPlanVsInspectConsistency:
    def test_action_count_matches_finding_count(self) -> None:
        from aeos.providers.supabase.rls import run_rls_inspect

        plan = run_rls_plan(FIXTURE_DIR)
        inspect = run_rls_inspect(FIXTURE_DIR)
        assert len(plan.actions) == len(inspect.findings)

    def test_migrations_scanned_matches(self) -> None:
        from aeos.providers.supabase.rls import run_rls_inspect

        plan = run_rls_plan(FIXTURE_DIR)
        inspect = run_rls_inspect(FIXTURE_DIR)
        assert plan.migrations_scanned == inspect.migrations_scanned
