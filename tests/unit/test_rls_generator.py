"""
Unit tests for the Supabase RLS Migration Generator (Sprint 2V).
"""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from aeos.cli import app
from aeos.providers.supabase.rls import run_rls_generate
from aeos.providers.supabase.rls.generator import (
    SQLBlock,
    _assemble_sql,
    _detect_has_role_call,
    _detect_tenant_column,
    _gen_auth_role_authenticated,
    _gen_combined,
    _gen_insert_no_with_check,
    _gen_missing_tenant_scope,
    _gen_no_delete_policy,
    _gen_no_policies,
    _gen_no_rls,
    _gen_select_too_permissive,
    _gen_update_no_with_check,
    _group_actions,
    _has_user_id,
    _is_permissive,
    _make_todo,
)
from aeos.providers.supabase.rls.inspector import RLSPolicy
from aeos.providers.supabase.rls.planner import RLSPlanAction

runner = CliRunner()

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "supabase_rls"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _pol(
    name: str = "test_pol",
    table: str = "test_table",
    command: str = "INSERT",
    using: str = "",
    check: str = "",
    source_file: str = "migrations/001.sql",
    source_line: int = 1,
) -> RLSPolicy:
    return RLSPolicy(
        name=name,
        table=table,
        command=command,
        using_expr=using,
        with_check_expr=check,
        source_file=source_file,
        source_line=source_line,
    )


def _action(
    priority: str = "HIGH",
    table: str = "test_table",
    policy: str = "test_pol",
    risk_type: str = "INSERT_NO_WITH_CHECK",
    severity: str = "WARNING",
    order: int = 1,
    problem: str = "Problem.",
    fix: str = "Fix it.",
    functional_impact: str = "Impact.",
    recommended_test: str = "Test it.",
    source_file: str = "migrations/001.sql",
) -> RLSPlanAction:
    return RLSPlanAction(
        order=order,
        priority=priority,
        table=table,
        policy=policy,
        risk_type=risk_type,
        severity=severity,
        problem=problem,
        fix=fix,
        functional_impact=functional_impact,
        recommended_test=recommended_test,
        source_file=source_file,
    )


# ---------------------------------------------------------------------------
# TestIsPermissive
# ---------------------------------------------------------------------------


class TestIsPermissive:
    def test_true_literal(self) -> None:
        assert _is_permissive("true") is True

    def test_true_upper(self) -> None:
        assert _is_permissive("TRUE") is True

    def test_true_whitespace(self) -> None:
        assert _is_permissive("  true  ") is True

    def test_auth_uid_is_not_null(self) -> None:
        assert _is_permissive("auth.uid() IS NOT NULL") is True

    def test_auth_uid_is_not_null_spaced(self) -> None:
        assert _is_permissive("auth . uid (  )   IS NOT NULL") is True

    def test_specific_condition_not_permissive(self) -> None:
        assert _is_permissive("auth.uid() = user_id") is False

    def test_has_role_not_permissive(self) -> None:
        assert _is_permissive("public.has_role(auth.uid(), 'agent'::app_role)") is False

    def test_empty_not_permissive(self) -> None:
        assert _is_permissive("") is False

    def test_commune_filter_not_permissive(self) -> None:
        assert _is_permissive("commune_id = (SELECT commune_id FROM profiles)") is False


# ---------------------------------------------------------------------------
# TestDetectTenantColumn
# ---------------------------------------------------------------------------


class TestDetectTenantColumn:
    def test_detects_commune_id(self) -> None:
        policies = [_pol(check="auth.uid() = user_id AND commune_id IS NOT NULL")]
        assert _detect_tenant_column(policies) == "commune_id"

    def test_detects_tenant_id_when_no_commune(self) -> None:
        policies = [_pol(using="tenant_id = auth.uid()")]
        assert _detect_tenant_column(policies) == "tenant_id"

    def test_prefers_commune_id_over_tenant_id(self) -> None:
        p1 = _pol(using="tenant_id = auth.uid()")
        p2 = _pol(using="commune_id = auth.uid()")
        assert _detect_tenant_column([p1, p2]) == "commune_id"

    def test_defaults_to_commune_id_when_absent(self) -> None:
        policies = [_pol(using="auth.uid() = user_id")]
        assert _detect_tenant_column(policies) == "commune_id"

    def test_detects_org_id(self) -> None:
        policies = [_pol(check="org_id IS NOT NULL AND auth.uid() = user_id")]
        assert _detect_tenant_column(policies) == "org_id"


# ---------------------------------------------------------------------------
# TestDetectHasRoleCall
# ---------------------------------------------------------------------------


class TestDetectHasRoleCall:
    def test_detects_has_role(self) -> None:
        policies = [_pol(using="public.has_role(auth.uid(), 'agent'::app_role)")]
        result = _detect_has_role_call(policies)
        assert result == "public.has_role(auth.uid(), 'agent'::app_role)"

    def test_returns_empty_when_absent(self) -> None:
        policies = [_pol(using="auth.uid() = user_id")]
        assert _detect_has_role_call(policies) == ""

    def test_detects_first_occurrence(self) -> None:
        p1 = _pol(using="auth.uid() = user_id")
        p2 = _pol(using="public.has_role(auth.uid(), 'admin'::app_role)")
        result = _detect_has_role_call([p1, p2])
        assert "has_role" in result

    def test_searches_both_using_and_check(self) -> None:
        p = _pol(check="public.has_role(auth.uid(), 'maire'::app_role)")
        assert _detect_has_role_call([p]) != ""


# ---------------------------------------------------------------------------
# TestHasUserId
# ---------------------------------------------------------------------------


class TestHasUserId:
    def test_detects_user_id_in_using(self) -> None:
        policies = [_pol(table="posts", using="auth.uid() = user_id")]
        assert _has_user_id(policies, "posts") is True

    def test_detects_user_id_in_check(self) -> None:
        policies = [_pol(table="posts", check="auth.uid() = user_id")]
        assert _has_user_id(policies, "posts") is True

    def test_returns_false_when_absent(self) -> None:
        policies = [_pol(table="posts", using="commune_id = auth.uid()")]
        assert _has_user_id(policies, "posts") is False

    def test_scoped_to_table(self) -> None:
        p_other = _pol(table="other", using="auth.uid() = user_id")
        assert _has_user_id([p_other], "posts") is False


# ---------------------------------------------------------------------------
# TestMakeTodo
# ---------------------------------------------------------------------------


class TestMakeTodo:
    def test_is_todo(self) -> None:
        block = _make_todo(_action(), "Cannot determine.")
        assert block.is_todo is True

    def test_sql_contains_todo_marker(self) -> None:
        block = _make_todo(_action(), "Cannot determine.")
        assert "TODO" in block.sql

    def test_sql_contains_priority(self) -> None:
        block = _make_todo(_action(priority="CRITICAL"), "reason")
        assert "CRITICAL" in block.sql

    def test_sql_contains_reason(self) -> None:
        block = _make_todo(_action(), "unique reason text")
        assert "unique reason text" in block.sql

    def test_metadata_carried(self) -> None:
        a = _action(priority="HIGH", table="foo", risk_type="NO_POLICIES")
        block = _make_todo(a, "reason")
        assert block.priority == "HIGH"
        assert block.table == "foo"
        assert block.risk_type == "NO_POLICIES"


# ---------------------------------------------------------------------------
# TestGenInsertNoWithCheck
# ---------------------------------------------------------------------------


class TestGenInsertNoWithCheck:
    def test_mirrors_using_as_check(self) -> None:
        policy = _pol(command="INSERT", using="auth.uid() = user_id")
        block = _gen_insert_no_with_check(_action(), policy, user_id_ok=True)
        assert "WITH CHECK" in block.sql
        assert "auth.uid() = user_id" in block.sql
        assert not block.is_todo

    def test_fallback_to_user_id_when_permissive_using(self) -> None:
        policy = _pol(command="INSERT", using="true")
        block = _gen_insert_no_with_check(_action(), policy, user_id_ok=True)
        assert "auth.uid() = user_id" in block.sql
        assert not block.is_todo

    def test_todo_when_permissive_and_no_user_id(self) -> None:
        policy = _pol(command="INSERT", using="auth.uid() IS NOT NULL")
        block = _gen_insert_no_with_check(_action(), policy, user_id_ok=False)
        assert block.is_todo

    def test_todo_when_policy_is_none(self) -> None:
        block = _gen_insert_no_with_check(_action(), None, user_id_ok=True)
        assert block.is_todo

    def test_todo_when_command_is_all(self) -> None:
        policy = _pol(command="ALL", using="auth.uid() = user_id")
        block = _gen_insert_no_with_check(_action(), policy, user_id_ok=True)
        assert block.is_todo

    def test_idempotent_drop_then_create(self) -> None:
        policy = _pol(
            name="my_policy",
            table="items",
            command="INSERT",
            using="auth.uid() = user_id",
        )
        block = _gen_insert_no_with_check(_action(), policy, user_id_ok=True)
        assert 'DROP POLICY IF EXISTS "my_policy" ON public.items' in block.sql
        assert 'CREATE POLICY "my_policy"' in block.sql

    def test_for_insert_not_select_or_update(self) -> None:
        policy = _pol(command="INSERT", using="auth.uid() = user_id")
        block = _gen_insert_no_with_check(_action(), policy, user_id_ok=True)
        assert "FOR INSERT" in block.sql
        assert "FOR SELECT" not in block.sql
        assert "FOR UPDATE" not in block.sql


# ---------------------------------------------------------------------------
# TestGenUpdateNoWithCheck
# ---------------------------------------------------------------------------


class TestGenUpdateNoWithCheck:
    def test_mirrors_using_as_both_clauses(self) -> None:
        policy = _pol(
            command="UPDATE",
            using="public.has_role(auth.uid(), 'agent'::app_role)",
        )
        block = _gen_update_no_with_check(_action(), policy, user_id_ok=True)
        assert "USING" in block.sql
        assert "WITH CHECK" in block.sql
        assert not block.is_todo

    def test_for_update(self) -> None:
        policy = _pol(command="UPDATE", using="auth.uid() = user_id")
        block = _gen_update_no_with_check(_action(), policy, user_id_ok=True)
        assert "FOR UPDATE" in block.sql

    def test_todo_when_permissive_and_no_user_id(self) -> None:
        policy = _pol(command="UPDATE", using="true")
        block = _gen_update_no_with_check(_action(), policy, user_id_ok=False)
        assert block.is_todo

    def test_todo_for_all_command(self) -> None:
        policy = _pol(command="ALL", using="auth.uid() = user_id")
        block = _gen_update_no_with_check(_action(), policy, user_id_ok=True)
        assert block.is_todo


# ---------------------------------------------------------------------------
# TestGenMissingTenantScope
# ---------------------------------------------------------------------------


class TestGenMissingTenantScope:
    def test_insert_adds_tenant_to_with_check(self) -> None:
        policy = _pol(
            command="INSERT",
            check="auth.uid() = user_id",
        )
        block = _gen_missing_tenant_scope(_action(), policy, tenant_col="commune_id")
        assert "commune_id" in block.sql
        assert "WITH CHECK" in block.sql
        assert not block.is_todo

    def test_update_adds_tenant_to_both(self) -> None:
        policy = _pol(
            command="UPDATE",
            using="auth.uid() = user_id",
            check="auth.uid() = user_id",
        )
        block = _gen_missing_tenant_scope(_action(), policy, tenant_col="commune_id")
        assert "USING" in block.sql
        assert "WITH CHECK" in block.sql
        assert "commune_id" in block.sql
        assert not block.is_todo

    def test_todo_for_all_command(self) -> None:
        policy = _pol(command="ALL", using="auth.uid() = user_id")
        block = _gen_missing_tenant_scope(_action(), policy, tenant_col="commune_id")
        assert block.is_todo

    def test_todo_for_select_command(self) -> None:
        policy = _pol(command="SELECT", using="auth.uid() = user_id")
        block = _gen_missing_tenant_scope(_action(), policy, tenant_col="commune_id")
        assert block.is_todo

    def test_warning_mentions_profiles(self) -> None:
        policy = _pol(command="INSERT", check="auth.uid() = user_id")
        block = _gen_missing_tenant_scope(_action(), policy, tenant_col="commune_id")
        assert "profiles" in block.warning.lower()

    def test_todo_when_policy_is_none(self) -> None:
        block = _gen_missing_tenant_scope(_action(), None, tenant_col="commune_id")
        assert block.is_todo

    def test_profiles_subquery_present(self) -> None:
        policy = _pol(command="INSERT", check="auth.uid() = user_id")
        block = _gen_missing_tenant_scope(_action(), policy, tenant_col="commune_id")
        assert "FROM public.profiles" in block.sql


# ---------------------------------------------------------------------------
# TestGenSelectTooPermissive
# ---------------------------------------------------------------------------


class TestGenSelectTooPermissive:
    def test_always_todo(self) -> None:
        policy = _pol(command="SELECT", using="true")
        block = _gen_select_too_permissive(
            _action(risk_type="SELECT_TOO_PERMISSIVE"), policy, tenant_col="commune_id"
        )
        assert block.is_todo

    def test_proposed_fix_commented_out(self) -> None:
        policy = _pol(command="SELECT", using="true")
        block = _gen_select_too_permissive(
            _action(risk_type="SELECT_TOO_PERMISSIVE"), policy, tenant_col="commune_id"
        )
        assert block.sql.startswith("--")

    def test_warning_present(self) -> None:
        policy = _pol(command="SELECT", using="true")
        block = _gen_select_too_permissive(
            _action(risk_type="SELECT_TOO_PERMISSIVE"), policy, tenant_col="commune_id"
        )
        assert block.warning != ""

    def test_todo_when_policy_is_none(self) -> None:
        block = _gen_select_too_permissive(
            _action(risk_type="SELECT_TOO_PERMISSIVE"), None, tenant_col="commune_id"
        )
        assert block.is_todo


# ---------------------------------------------------------------------------
# TestGenNoDeletePolicy
# ---------------------------------------------------------------------------


class TestGenNoDeletePolicy:
    def test_generates_self_delete(self) -> None:
        a = _action(risk_type="NO_DELETE_POLICY", policy="", table="posts")
        block = _gen_no_delete_policy(a, has_role_call="")
        assert "FOR DELETE" in block.sql
        assert "auth.uid() = user_id" in block.sql
        assert not block.is_todo

    def test_uses_detected_has_role(self) -> None:
        a = _action(risk_type="NO_DELETE_POLICY", policy="", table="posts")
        has_role = "public.has_role(auth.uid(), 'agent'::app_role)"
        block = _gen_no_delete_policy(a, has_role_call=has_role)
        assert has_role in block.sql
        assert "-- TODO" not in block.sql.split(has_role)[0]

    def test_moderator_todo_when_no_has_role(self) -> None:
        a = _action(risk_type="NO_DELETE_POLICY", policy="", table="posts")
        block = _gen_no_delete_policy(a, has_role_call="")
        assert "TODO" in block.sql

    def test_warning_present(self) -> None:
        a = _action(risk_type="NO_DELETE_POLICY", policy="", table="posts")
        block = _gen_no_delete_policy(a, has_role_call="")
        assert block.warning != ""

    def test_policy_names_use_table(self) -> None:
        a = _action(risk_type="NO_DELETE_POLICY", policy="", table="forum_posts")
        block = _gen_no_delete_policy(a, has_role_call="")
        assert "forum_posts_delete_own" in block.sql


# ---------------------------------------------------------------------------
# TestGenNoRLS
# ---------------------------------------------------------------------------


class TestGenNoRLS:
    def test_enables_rls(self) -> None:
        a = _action(risk_type="NO_RLS", policy="", table="items")
        block = _gen_no_rls(a)
        assert "ENABLE ROW LEVEL SECURITY" in block.sql
        assert "items" in block.sql
        assert not block.is_todo

    def test_includes_todo_policy_example(self) -> None:
        a = _action(risk_type="NO_RLS", policy="", table="items")
        block = _gen_no_rls(a)
        assert "TODO" in block.sql

    def test_no_warning_for_rls_enable(self) -> None:
        a = _action(risk_type="NO_RLS", policy="", table="items")
        block = _gen_no_rls(a)
        assert block.warning == ""


# ---------------------------------------------------------------------------
# TestGenNoPolicies
# ---------------------------------------------------------------------------


class TestGenNoPolicies:
    def test_is_todo(self) -> None:
        a = _action(risk_type="NO_POLICIES", policy="", table="items")
        block = _gen_no_policies(a)
        assert block.is_todo

    def test_mentions_table(self) -> None:
        a = _action(risk_type="NO_POLICIES", policy="", table="secret_data")
        block = _gen_no_policies(a)
        assert "secret_data" in block.sql


# ---------------------------------------------------------------------------
# TestGenAuthRoleAuthenticated
# ---------------------------------------------------------------------------


class TestGenAuthRoleAuthenticated:
    def test_is_todo(self) -> None:
        policy = _pol(command="INSERT", check="auth.role() = 'authenticated'")
        a = _action(risk_type="AUTH_ROLE_AUTHENTICATED")
        block = _gen_auth_role_authenticated(a, policy)
        assert block.is_todo

    def test_mentions_policy_name(self) -> None:
        policy = _pol(name="my_insert_policy", command="INSERT")
        a = _action(risk_type="AUTH_ROLE_AUTHENTICATED")
        block = _gen_auth_role_authenticated(a, policy)
        assert "my_insert_policy" in block.sql

    def test_todo_when_policy_is_none(self) -> None:
        a = _action(risk_type="AUTH_ROLE_AUTHENTICATED")
        block = _gen_auth_role_authenticated(a, None)
        assert block.is_todo


# ---------------------------------------------------------------------------
# TestGenCombined
# ---------------------------------------------------------------------------


class TestGenCombined:
    def test_update_with_check_and_tenant(self) -> None:
        policy = _pol(
            name="update_agents",
            table="actes",
            command="UPDATE",
            using="public.has_role(auth.uid(), 'agent'::app_role)",
        )
        a1 = _action(
            priority="HIGH",
            table="actes",
            policy="update_agents",
            risk_type="UPDATE_NO_WITH_CHECK",
        )
        a2 = _action(
            priority="HIGH",
            table="actes",
            policy="update_agents",
            risk_type="MISSING_TENANT_SCOPE",
        )
        block = _gen_combined([a1, a2], policy, "commune_id", user_id_ok=False)
        assert not block.is_todo
        assert "WITH CHECK" in block.sql
        assert "commune_id" in block.sql
        assert "USING" in block.sql

    def test_insert_with_check_and_tenant(self) -> None:
        policy = _pol(
            name="insert_own",
            table="items",
            command="INSERT",
            using="auth.uid() = user_id",
        )
        a1 = _action(
            priority="HIGH",
            table="items",
            policy="insert_own",
            risk_type="INSERT_NO_WITH_CHECK",
        )
        a2 = _action(
            priority="HIGH",
            table="items",
            policy="insert_own",
            risk_type="MISSING_TENANT_SCOPE",
        )
        block = _gen_combined([a1, a2], policy, "commune_id", user_id_ok=True)
        assert not block.is_todo
        assert "WITH CHECK" in block.sql
        assert "commune_id" in block.sql

    def test_todo_when_policy_is_none(self) -> None:
        a1 = _action(risk_type="UPDATE_NO_WITH_CHECK")
        a2 = _action(risk_type="MISSING_TENANT_SCOPE")
        block = _gen_combined([a1, a2], None, "commune_id", user_id_ok=True)
        assert block.is_todo

    def test_todo_when_all_command(self) -> None:
        policy = _pol(command="ALL", using="auth.uid() = user_id")
        a1 = _action(risk_type="UPDATE_NO_WITH_CHECK")
        a2 = _action(risk_type="MISSING_TENANT_SCOPE")
        block = _gen_combined([a1, a2], policy, "commune_id", user_id_ok=True)
        assert block.is_todo

    def test_todo_when_permissive_using_and_no_user_id(self) -> None:
        policy = _pol(command="UPDATE", using="true")
        a1 = _action(risk_type="UPDATE_NO_WITH_CHECK")
        a2 = _action(risk_type="MISSING_TENANT_SCOPE")
        block = _gen_combined([a1, a2], policy, "commune_id", user_id_ok=False)
        assert block.is_todo

    def test_risk_type_includes_both_rules(self) -> None:
        policy = _pol(command="UPDATE", using="auth.uid() = user_id")
        a1 = _action(risk_type="UPDATE_NO_WITH_CHECK")
        a2 = _action(risk_type="MISSING_TENANT_SCOPE")
        block = _gen_combined([a1, a2], policy, "commune_id", user_id_ok=True)
        assert "UPDATE_NO_WITH_CHECK" in block.risk_type
        assert "MISSING_TENANT_SCOPE" in block.risk_type


# ---------------------------------------------------------------------------
# TestGroupActions
# ---------------------------------------------------------------------------


class TestGroupActions:
    def test_single_actions_ungrouped(self) -> None:
        a1 = _action(table="t1", policy="p1", risk_type="NO_RLS", priority="CRITICAL")
        a2 = _action(table="t2", policy="p2", risk_type="NO_RLS", priority="CRITICAL")
        groups = _group_actions([a1, a2])
        assert len(groups) == 2
        assert all(len(g) == 1 for g in groups)

    def test_same_table_policy_grouped(self) -> None:
        a1 = _action(table="t", policy="p", risk_type="UPDATE_NO_WITH_CHECK")
        a2 = _action(table="t", policy="p", risk_type="MISSING_TENANT_SCOPE")
        groups = _group_actions([a1, a2])
        assert len(groups) == 1
        assert len(groups[0]) == 2

    def test_table_level_actions_not_grouped(self) -> None:
        a1 = _action(table="t", policy="", risk_type="NO_RLS")
        a2 = _action(table="t", policy="", risk_type="NO_DELETE_POLICY")
        groups = _group_actions([a1, a2])
        assert len(groups) == 2

    def test_different_policies_same_table_not_grouped(self) -> None:
        a1 = _action(table="t", policy="pol1", risk_type="UPDATE_NO_WITH_CHECK")
        a2 = _action(table="t", policy="pol2", risk_type="MISSING_TENANT_SCOPE")
        groups = _group_actions([a1, a2])
        assert len(groups) == 2

    def test_different_priorities_not_grouped(self) -> None:
        a1 = _action(priority="CRITICAL", table="t", policy="p", risk_type="A")
        a2 = _action(priority="HIGH", table="t", policy="p", risk_type="B")
        groups = _group_actions([a1, a2])
        assert len(groups) == 2


# ---------------------------------------------------------------------------
# TestAssembleSQL
# ---------------------------------------------------------------------------


class TestAssembleSQL:
    _DEFAULT_SQL = (
        "-- FIX\n"
        'DROP POLICY IF EXISTS "p" ON public.t;\n'
        'CREATE POLICY "p"\n'
        "  ON public.t\n"
        "  FOR UPDATE\n"
        "  USING (auth.uid() = user_id)\n"
        "  WITH CHECK (auth.uid() = user_id);"
    )

    def _make_block(
        self,
        priority: str = "HIGH",
        table: str = "t",
        policy: str = "p",
        risk_type: str = "UPDATE_NO_WITH_CHECK",
        sql: str = "",
        is_todo: bool = False,
        warning: str = "",
    ) -> SQLBlock:
        if not sql:
            sql = self._DEFAULT_SQL
        return SQLBlock(
            priority=priority,
            table=table,
            policy=policy,
            risk_type=risk_type,
            sql=sql,
            is_todo=is_todo,
            warning=warning,
        )

    def test_header_present(self) -> None:
        sql = _assemble_sql([self._make_block()], Path("/projects/my-app"), False)
        assert "AEOS RLS Migration Proposal" in sql

    def test_begin_commit_present(self) -> None:
        sql = _assemble_sql([self._make_block()], Path("/projects/my-app"), False)
        assert "BEGIN;" in sql
        assert "COMMIT;" in sql

    def test_scope_critical_high_only(self) -> None:
        sql = _assemble_sql([self._make_block()], Path("/projects/my-app"), False)
        assert "CRITICAL + HIGH" in sql
        assert "MEDIUM" not in sql.split("CRITICAL + HIGH")[1].split("\n")[0]

    def test_scope_with_medium(self) -> None:
        sql = _assemble_sql([self._make_block()], Path("/projects/my-app"), True)
        assert "CRITICAL + HIGH + MEDIUM" in sql

    def test_warning_appended(self) -> None:
        block = self._make_block(warning="Check profiles table.")
        sql = _assemble_sql([block], Path("/projects/my-app"), False)
        assert "WARNING: Check profiles table." in sql

    def test_priority_section_header(self) -> None:
        block = self._make_block(priority="CRITICAL")
        sql = _assemble_sql([block], Path("/projects/my-app"), False)
        assert "CRITICAL" in sql

    def test_not_applied(self) -> None:
        sql = _assemble_sql([self._make_block()], Path("/projects/my-app"), False)
        assert "NOT applied" in sql

    def test_applied_false_in_result(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        assert result.applied is False

    def test_read_only_in_result(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        assert result.read_only is True


# ---------------------------------------------------------------------------
# TestRunRLSGenerateOnFixture
# ---------------------------------------------------------------------------


class TestRunRLSGenerateOnFixture:
    def test_returns_result(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        assert result is not None

    def test_path_is_absolute(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        assert result.path.is_absolute()

    def test_migrations_scanned_nonzero(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        assert result.migrations_scanned > 0

    def test_blocks_generated(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        assert result.summary.total_blocks > 0

    def test_applied_is_always_false(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        assert result.applied is False

    def test_read_only_is_true(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        assert result.read_only is True

    def test_no_env_secrets_in_sql(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        for secret in ("password", "anon_key", "service_role"):
            assert secret not in result.generated_sql

    def test_generated_sql_contains_begin_commit(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        assert "BEGIN;" in result.generated_sql
        assert "COMMIT;" in result.generated_sql

    def test_generated_sql_contains_header(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        assert "AEOS RLS Migration Proposal" in result.generated_sql

    def test_include_medium_adds_blocks(self) -> None:
        result_default = run_rls_generate(FIXTURE_DIR, include_medium=False)
        result_medium = run_rls_generate(FIXTURE_DIR, include_medium=True)
        assert result_medium.summary.total_blocks >= result_default.summary.total_blocks

    def test_no_rls_table_generates_alter(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        assert "ENABLE ROW LEVEL SECURITY" in result.generated_sql

    def test_test_plan_nonempty(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        assert len(result.test_plan) > 0

    def test_auto_generated_plus_todos_equals_total(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        assert (
            result.summary.auto_generated + result.summary.manual_todos
            == result.summary.total_blocks
        )

    def test_status_inherits_from_inspector(self) -> None:
        result_inspect = run_rls_generate(FIXTURE_DIR)
        assert result_inspect.status in {"OK", "WARNING", "ERROR"}

    def test_by_priority_keys_present(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        assert "CRITICAL" in result.summary.by_priority
        assert "HIGH" in result.summary.by_priority

    def test_no_migrations_returns_empty_result(self, tmp_path: Path) -> None:
        (tmp_path / "supabase" / "migrations").mkdir(parents=True)
        result = run_rls_generate(tmp_path)
        assert result.summary.total_blocks == 0
        assert result.applied is False


# ---------------------------------------------------------------------------
# TestAntiLeakage
# ---------------------------------------------------------------------------


class TestAntiLeakage:
    def test_env_file_not_read(self, tmp_path: Path) -> None:
        mig_dir = tmp_path / "supabase" / "migrations"
        mig_dir.mkdir(parents=True)
        (mig_dir / "001_test.sql").write_text(
            "CREATE TABLE public.items (id uuid PRIMARY KEY);\n"
        )
        env_file = tmp_path / ".env"
        env_file.write_text(
            "SUPABASE_URL=https://secret.supabase.co\n"
            "ANON_KEY=super_secret_anon_key_12345\n"
        )
        result = run_rls_generate(tmp_path)
        assert "super_secret_anon_key_12345" not in result.generated_sql
        for block in result.blocks:
            assert "super_secret_anon_key_12345" not in block.sql
        env_file.unlink()

    def test_applied_never_true(self) -> None:
        result = run_rls_generate(FIXTURE_DIR)
        assert result.applied is False


# ---------------------------------------------------------------------------
# TestCLIGenerateTextOutput
# ---------------------------------------------------------------------------


class TestCLIGenerateTextOutput:
    def test_command_exists(self) -> None:
        result = runner.invoke(
            app,
            ["supabase", "rls", "generate", "--path", str(FIXTURE_DIR)],
        )
        assert result.exit_code in (0, 1)

    def test_output_contains_header(self) -> None:
        result = runner.invoke(
            app,
            ["supabase", "rls", "generate", "--path", str(FIXTURE_DIR)],
        )
        assert "Supabase RLS Migration Generator" in result.output

    def test_output_contains_sql(self) -> None:
        result = runner.invoke(
            app,
            ["supabase", "rls", "generate", "--path", str(FIXTURE_DIR)],
        )
        assert "BEGIN;" in result.output or "No SQL blocks" in result.output

    def test_output_read_only_notice(self) -> None:
        result = runner.invoke(
            app,
            ["supabase", "rls", "generate", "--path", str(FIXTURE_DIR)],
        )
        assert "Read-only" in result.output

    def test_include_medium_flag_accepted(self) -> None:
        result = runner.invoke(
            app,
            [
                "supabase",
                "rls",
                "generate",
                "--path",
                str(FIXTURE_DIR),
                "--include-medium",
            ],
        )
        assert result.exit_code in (0, 1)

    def test_nonexistent_path_exits_1(self) -> None:
        result = runner.invoke(
            app,
            ["supabase", "rls", "generate", "--path", "/nonexistent/path/xyz"],
        )
        assert result.exit_code == 1

    def test_output_contains_test_plan(self) -> None:
        result = runner.invoke(
            app,
            ["supabase", "rls", "generate", "--path", str(FIXTURE_DIR)],
        )
        assert "Test Plan" in result.output or "No SQL blocks" in result.output


# ---------------------------------------------------------------------------
# TestCLIGenerateJSONOutput
# ---------------------------------------------------------------------------


class TestCLIGenerateJSONOutput:
    def _run_json(self, extra: list[str] | None = None) -> dict:  # type: ignore[type-arg]
        args = [
            "supabase",
            "rls",
            "generate",
            "--path",
            str(FIXTURE_DIR),
            "--json",
        ]
        if extra:
            args += extra
        result = runner.invoke(app, args)
        return json.loads(result.output)  # type: ignore[no-any-return]

    def test_valid_json(self) -> None:
        self._run_json()  # would raise if invalid JSON

    def test_applied_is_false(self) -> None:
        data = self._run_json()
        assert data["applied"] is False

    def test_read_only_is_true(self) -> None:
        data = self._run_json()
        assert data["read_only"] is True

    def test_status_field_present(self) -> None:
        data = self._run_json()
        assert "status" in data

    def test_summary_fields_present(self) -> None:
        data = self._run_json()
        s = data["summary"]
        assert "total_blocks" in s
        assert "auto_generated" in s
        assert "manual_todos" in s
        assert "by_priority" in s
        assert "include_medium" in s

    def test_generated_sql_present(self) -> None:
        data = self._run_json()
        assert "generated_sql" in data

    def test_warnings_present(self) -> None:
        data = self._run_json()
        assert "warnings" in data
        assert isinstance(data["warnings"], list)

    def test_test_plan_present(self) -> None:
        data = self._run_json()
        assert "test_plan" in data
        assert isinstance(data["test_plan"], list)

    def test_include_medium_reflected_in_summary(self) -> None:
        data = self._run_json(["--include-medium"])
        assert data["summary"]["include_medium"] is True

    def test_no_secrets_in_json_output(self) -> None:
        data = self._run_json()
        raw = json.dumps(data)
        for secret in ("password", "service_role", "anon_key"):
            assert secret not in raw
