"""
Supabase RLS Migration Generator — transforms RLS Plan actions into
a proposed SQL migration.

Generated SQL is printed, never written to disk or applied.
Read-only. No network access. No secret reads. No file modification.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from aeos.providers.supabase.rls.inspector import RLSPolicy, run_rls_inspect
from aeos.providers.supabase.rls.planner import RLSPlanAction, run_rls_plan

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PRIORITY_ORDER: dict[str, int] = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

_TRUE_RE = re.compile(r"^\s*true\s*$", re.IGNORECASE)
_AUTH_UID_NOT_NULL_RE = re.compile(
    r"auth\s*\.\s*uid\s*\(\s*\)\s+IS\s+NOT\s+NULL", re.IGNORECASE
)
_USER_ID_RE = re.compile(r"\buser_id\b", re.IGNORECASE)
_HAS_ROLE_RE = re.compile(
    r"(public\.has_role\((?:[^()]|\([^)]*\))*\))",
    re.IGNORECASE,
)

_TENANT_PRIORITY = [
    "commune_id",
    "tenant_id",
    "org_id",
    "organization_id",
    "municipality_id",
]

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class SQLBlock:
    priority: str  # CRITICAL | HIGH | MEDIUM
    table: str
    policy: str  # policy name, or "" for table-level blocks
    risk_type: str  # rule name(s), joined with " + " for combined
    sql: str  # generated SQL or commented TODO
    is_todo: bool  # True when manual review is required
    warning: str = ""  # optional warning message


@dataclass
class RLSGenerateSummary:
    total_blocks: int
    auto_generated: int  # blocks with executable SQL
    manual_todos: int  # blocks that need manual review
    by_priority: dict[str, int]
    include_medium: bool


@dataclass
class RLSGenerateResult:
    path: Path
    status: str  # OK | WARNING | ERROR
    migrations_scanned: int
    summary: RLSGenerateSummary
    blocks: list[SQLBlock] = field(default_factory=list)
    generated_sql: str = ""
    warnings: list[str] = field(default_factory=list)
    test_plan: list[str] = field(default_factory=list)
    read_only: bool = True
    applied: bool = False


# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------


def _is_permissive(expr: str) -> bool:
    """True if the expression grants access to any authenticated user."""
    return bool(_TRUE_RE.match(expr)) or bool(_AUTH_UID_NOT_NULL_RE.match(expr))


def _detect_tenant_column(policies: list[RLSPolicy]) -> str:
    """Return the first tenant column referenced in any policy expression."""
    for col in _TENANT_PRIORITY:
        pattern = re.compile(rf"\b{col}\b", re.IGNORECASE)
        if any(pattern.search(p.using_expr + p.with_check_expr) for p in policies):
            return col
    return "commune_id"


def _detect_has_role_call(policies: list[RLSPolicy]) -> str:
    """Return a has_role() call found in any policy expression, or ""."""
    for p in policies:
        m = _HAS_ROLE_RE.search(p.using_expr + p.with_check_expr)
        if m:
            return m.group(1)
    return ""


def _has_user_id(policies: list[RLSPolicy], table: str) -> bool:
    """True if any policy on this table references user_id."""
    return any(
        _USER_ID_RE.search(p.using_expr + p.with_check_expr)
        for p in policies
        if p.table == table
    )


# ---------------------------------------------------------------------------
# SQL helpers
# ---------------------------------------------------------------------------


def _q(name: str) -> str:
    """Return a double-quoted SQL identifier."""
    return f'"{name}"'


def _make_todo(action: RLSPlanAction, reason: str) -> SQLBlock:
    """Build a TODO block when safe SQL cannot be generated automatically."""
    target = action.policy or "(table-level)"
    comment = "\n".join(
        [
            f"-- TODO [{action.priority}] {action.risk_type}: {action.table}"
            f" — {target}",
            f"-- Reason: {reason}",
            f"-- Problem: {action.problem}",
            f"-- Fix: {action.fix}",
        ]
    )
    return SQLBlock(
        priority=action.priority,
        table=action.table,
        policy=action.policy,
        risk_type=action.risk_type,
        sql=comment,
        is_todo=True,
    )


def _tenant_ref(tenant_col: str) -> str:
    # tenant_col is always from a fixed list of known column names
    return f"(SELECT {tenant_col} FROM public.profiles WHERE id = auth.uid())"  # noqa: S608


# ---------------------------------------------------------------------------
# Per-risk generators (single-rule)
# ---------------------------------------------------------------------------


def _gen_insert_no_with_check(
    action: RLSPlanAction,
    policy: RLSPolicy | None,
    user_id_ok: bool,
) -> SQLBlock:
    if policy is None:
        return _make_todo(action, "Original policy not found.")
    if policy.command == "ALL":
        return _make_todo(
            action,
            "ALL policy — split into INSERT/UPDATE/SELECT/DELETE and add"
            " WITH CHECK to INSERT.",
        )
    using = policy.using_expr
    if using and not _is_permissive(using):
        with_check = using
    elif user_id_ok:
        with_check = "auth.uid() = user_id"
    else:
        return _make_todo(
            action,
            "Cannot determine safe WITH CHECK — add WITH CHECK"
            " (auth.uid() = user_id) manually.",
        )
    sql = "\n".join(
        [
            f"-- [FIX] INSERT_NO_WITH_CHECK on {_q(policy.table)}",
            f"DROP POLICY IF EXISTS {_q(policy.name)} ON public.{policy.table};",
            f"CREATE POLICY {_q(policy.name)}",
            f"  ON public.{policy.table}",
            "  FOR INSERT",
            f"  WITH CHECK ({with_check});",
        ]
    )
    return SQLBlock(
        priority=action.priority,
        table=action.table,
        policy=action.policy,
        risk_type=action.risk_type,
        sql=sql,
        is_todo=False,
    )


def _gen_update_no_with_check(
    action: RLSPlanAction,
    policy: RLSPolicy | None,
    user_id_ok: bool,
) -> SQLBlock:
    if policy is None:
        return _make_todo(action, "Original policy not found.")
    if policy.command == "ALL":
        return _make_todo(
            action,
            "ALL policy — split into INSERT/UPDATE/SELECT/DELETE and add"
            " WITH CHECK to UPDATE.",
        )
    using = policy.using_expr
    if using and not _is_permissive(using):
        expr = using
    elif user_id_ok:
        expr = "auth.uid() = user_id"
    else:
        return _make_todo(
            action,
            "Cannot determine safe WITH CHECK — mirror the USING clause manually.",
        )
    sql = "\n".join(
        [
            f"-- [FIX] UPDATE_NO_WITH_CHECK on {_q(policy.table)}",
            f"DROP POLICY IF EXISTS {_q(policy.name)} ON public.{policy.table};",
            f"CREATE POLICY {_q(policy.name)}",
            f"  ON public.{policy.table}",
            "  FOR UPDATE",
            f"  USING ({expr})",
            f"  WITH CHECK ({expr});",
        ]
    )
    return SQLBlock(
        priority=action.priority,
        table=action.table,
        policy=action.policy,
        risk_type=action.risk_type,
        sql=sql,
        is_todo=False,
    )


def _gen_missing_tenant_scope(
    action: RLSPlanAction,
    policy: RLSPolicy | None,
    tenant_col: str,
) -> SQLBlock:
    if policy is None:
        return _make_todo(action, "Original policy not found.")
    if policy.command == "ALL":
        return _make_todo(
            action,
            f"ALL policy — split and add {tenant_col} scope to INSERT/UPDATE.",
        )
    ref = _tenant_ref(tenant_col)
    tenant_clause = f"{tenant_col} = {ref}"
    warning = (
        f"Verify public.profiles has a {tenant_col} column"
        " matching this table's tenant key."
    )
    if policy.command == "INSERT":
        base = policy.with_check_expr or policy.using_expr
        if not base:
            return _make_todo(action, "No base expression to extend.")
        new_check = f"{base}\n    AND {tenant_clause}"
        sql = "\n".join(
            [
                f"-- [FIX] MISSING_TENANT_SCOPE on {_q(policy.table)} (INSERT)",
                f"DROP POLICY IF EXISTS {_q(policy.name)} ON public.{policy.table};",
                f"CREATE POLICY {_q(policy.name)}",
                f"  ON public.{policy.table}",
                "  FOR INSERT",
                f"  WITH CHECK ({new_check});",
            ]
        )
    elif policy.command == "UPDATE":
        using_base = policy.using_expr
        check_base = policy.with_check_expr or policy.using_expr
        if not using_base:
            return _make_todo(action, "No USING expression to extend.")
        new_using = f"{using_base}\n    AND {tenant_clause}"
        new_check = f"{check_base}\n    AND {tenant_clause}"
        sql = "\n".join(
            [
                f"-- [FIX] MISSING_TENANT_SCOPE on {_q(policy.table)} (UPDATE)",
                f"DROP POLICY IF EXISTS {_q(policy.name)} ON public.{policy.table};",
                f"CREATE POLICY {_q(policy.name)}",
                f"  ON public.{policy.table}",
                "  FOR UPDATE",
                f"  USING ({new_using})",
                f"  WITH CHECK ({new_check});",
            ]
        )
    else:
        return _make_todo(
            action, f"Cannot auto-fix {tenant_col} scope for {policy.command}."
        )
    return SQLBlock(
        priority=action.priority,
        table=action.table,
        policy=action.policy,
        risk_type=action.risk_type,
        sql=sql,
        is_todo=False,
        warning=warning,
    )


def _gen_select_too_permissive(
    action: RLSPlanAction,
    policy: RLSPolicy | None,
    tenant_col: str,
) -> SQLBlock:
    """Always a TODO — SELECT scope change requires careful review."""
    if policy is None:
        return _make_todo(action, "Original policy not found.")
    ref = _tenant_ref(tenant_col)
    scope = f"{tenant_col} = {ref}"
    proposed = "\n".join(
        [
            "-- Proposed fix (verify before applying):",
            f"-- DROP POLICY IF EXISTS {_q(policy.name)} ON public.{policy.table};",
            f"-- CREATE POLICY {_q(policy.name)}",
            f"--   ON public.{policy.table}",
            "--   FOR SELECT",
            f"--   USING ({scope});",
            f"-- Impact: Users without matching {tenant_col} will lose access.",
            "-- Test: Verify all user roles can still reach their data.",
        ]
    )
    comment = "\n".join(
        [
            f"-- TODO [{action.priority}] SELECT_TOO_PERMISSIVE: {_q(policy.table)}",
            f"-- Policy {_q(policy.name)} exposes all rows to authenticated users.",
            proposed,
        ]
    )
    return SQLBlock(
        priority=action.priority,
        table=action.table,
        policy=action.policy,
        risk_type=action.risk_type,
        sql=comment,
        is_todo=True,
        warning=(
            "SELECT scope change requires careful testing before applying"
            " — verify access for all user roles."
        ),
    )


def _gen_no_delete_policy(
    action: RLSPlanAction,
    has_role_call: str,
) -> SQLBlock:
    table = action.table
    self_delete = "\n".join(
        [
            f"-- [FIX] NO_DELETE_POLICY: self-delete on {_q(table)}",
            f"CREATE POLICY {_q(f'{table}_delete_own')}",
            f"  ON public.{table}",
            "  FOR DELETE",
            "  USING (auth.uid() = user_id);",
        ]
    )
    if has_role_call:
        mod_lines = [
            "-- Moderator DELETE (uses detected role-check pattern)",
            f"CREATE POLICY {_q(f'{table}_delete_agents')}",
            f"  ON public.{table}",
            "  FOR DELETE",
            f"  USING ({has_role_call});",
        ]
    else:
        mod_lines = [
            f"-- TODO: Add moderator DELETE for {_q(table)}.",
            "-- Example:",
            f"-- CREATE POLICY {_q(f'{table}_delete_moderator')}",
            f"--   ON public.{table}",
            "--   FOR DELETE",
            "--   USING (/* your role check here */);",
        ]
    sql = self_delete + "\n\n" + "\n".join(mod_lines)
    return SQLBlock(
        priority=action.priority,
        table=action.table,
        policy="",
        risk_type=action.risk_type,
        sql=sql,
        is_todo=False,
        warning=(
            "Verify 'user_id' exists on this table and the moderator"
            " role check matches your project."
        ),
    )


def _gen_no_rls(action: RLSPlanAction) -> SQLBlock:
    table = action.table
    sql = "\n".join(
        [
            f"-- [FIX] NO_RLS: Enable RLS on {_q(table)}",
            f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;",
            f"-- TODO: Add appropriate policies for {_q(table)}.",
            "-- Example:",
            f"-- CREATE POLICY {_q(f'{table}_select_own')}",
            f"--   ON public.{table}",
            "--   FOR SELECT",
            "--   USING (auth.uid() = user_id);",
        ]
    )
    return SQLBlock(
        priority=action.priority,
        table=action.table,
        policy="",
        risk_type=action.risk_type,
        sql=sql,
        is_todo=False,
    )


def _gen_no_policies(action: RLSPlanAction) -> SQLBlock:
    table = action.table
    comment = "\n".join(
        [
            f"-- TODO [HIGH] NO_POLICIES: {_q(table)} has RLS but no policies.",
            "-- All access is currently blocked. Add appropriate policies.",
            "-- Example:",
            f"-- CREATE POLICY {_q(f'{table}_select_own')}",
            f"--   ON public.{table}",
            "--   FOR SELECT",
            "--   USING (auth.uid() = user_id);",
        ]
    )
    return SQLBlock(
        priority=action.priority,
        table=action.table,
        policy="",
        risk_type=action.risk_type,
        sql=comment,
        is_todo=True,
    )


def _gen_auth_role_authenticated(
    action: RLSPlanAction,
    policy: RLSPolicy | None,
) -> SQLBlock:
    if policy is None:
        return _make_todo(action, "Original policy not found.")
    comment = "\n".join(
        [
            f"-- TODO [MEDIUM] AUTH_ROLE_AUTHENTICATED: {_q(policy.table)}",
            f"-- Policy {_q(policy.name)} uses auth.role() = 'authenticated'.",
            "-- Replace with a specific ownership condition. Example:",
            f"-- DROP POLICY IF EXISTS {_q(policy.name)} ON public.{policy.table};",
            f"-- CREATE POLICY {_q(policy.name)}",
            f"--   ON public.{policy.table}",
            f"--   FOR {policy.command}",
            "--   USING (auth.uid() = user_id);",
        ]
    )
    return SQLBlock(
        priority=action.priority,
        table=action.table,
        policy=action.policy,
        risk_type=action.risk_type,
        sql=comment,
        is_todo=True,
    )


# ---------------------------------------------------------------------------
# Combined-fix generator (multiple rules on same policy)
# ---------------------------------------------------------------------------


def _gen_combined(
    group: list[RLSPlanAction],
    policy: RLSPolicy | None,
    tenant_col: str,
    user_id_ok: bool,
) -> SQLBlock:
    """
    Handle multiple rules on the same (table, policy) in one SQL block.
    Common case: {INSERT|UPDATE}_NO_WITH_CHECK + MISSING_TENANT_SCOPE.
    """
    rules = frozenset(a.risk_type for a in group)
    primary = group[0]

    if policy is None:
        return _make_todo(
            primary,
            f"Multiple issues ({', '.join(sorted(rules))}) — manual review.",
        )
    if policy.command == "ALL":
        return _make_todo(
            primary,
            f"ALL policy with multiple issues ({', '.join(sorted(rules))})"
            " — split by command first.",
        )

    command = policy.command
    using = policy.using_expr
    check = policy.with_check_expr

    has_check_fix = bool(rules & {"INSERT_NO_WITH_CHECK", "UPDATE_NO_WITH_CHECK"})
    needs_tenant = "MISSING_TENANT_SCOPE" in rules

    # Step 1: ensure WITH CHECK exists
    if has_check_fix:
        if using and not _is_permissive(using):
            check = using
        elif user_id_ok:
            check = "auth.uid() = user_id"
        else:
            return _make_todo(
                primary, "Cannot determine safe WITH CHECK — manual review."
            )

    # Step 2: add tenant scope to both USING and WITH CHECK
    if needs_tenant:
        ref = _tenant_ref(tenant_col)
        tenant_clause = f"{tenant_col} = {ref}"
        if using and not _is_permissive(using):
            using = f"{using}\n    AND {tenant_clause}"
        if check and not _is_permissive(check):
            check = f"{check}\n    AND {tenant_clause}"
        elif not check:
            check = tenant_clause

    rules_str = " + ".join(sorted(rules))
    lines = [
        f"-- [FIX] {rules_str} on {_q(policy.table)}",
        f"DROP POLICY IF EXISTS {_q(policy.name)} ON public.{policy.table};",
        f"CREATE POLICY {_q(policy.name)}",
        f"  ON public.{policy.table}",
        f"  FOR {command}",
    ]
    if command in ("SELECT", "UPDATE") and using:
        lines.append(f"  USING ({using})")
    if command in ("INSERT", "UPDATE") and check:
        lines.append(f"  WITH CHECK ({check});")
    else:
        lines[-1] += ";"

    warning = (
        f"Verify public.profiles has a {tenant_col} column." if needs_tenant else ""
    )
    return SQLBlock(
        priority=primary.priority,
        table=primary.table,
        policy=primary.policy,
        risk_type=rules_str,
        sql="\n".join(lines),
        is_todo=False,
        warning=warning,
    )


# ---------------------------------------------------------------------------
# Single-action dispatch
# ---------------------------------------------------------------------------


def _dispatch_single(
    action: RLSPlanAction,
    policy: RLSPolicy | None,
    tenant_col: str,
    has_role_call: str,
    user_id_ok: bool,
) -> SQLBlock:
    rule = action.risk_type
    if rule == "INSERT_NO_WITH_CHECK":
        return _gen_insert_no_with_check(action, policy, user_id_ok)
    if rule == "UPDATE_NO_WITH_CHECK":
        return _gen_update_no_with_check(action, policy, user_id_ok)
    if rule == "MISSING_TENANT_SCOPE":
        return _gen_missing_tenant_scope(action, policy, tenant_col)
    if rule in ("SELECT_TOO_PERMISSIVE", "SENSITIVE_TABLE_OPEN_SELECT"):
        return _gen_select_too_permissive(action, policy, tenant_col)
    if rule == "NO_DELETE_POLICY":
        return _gen_no_delete_policy(action, has_role_call)
    if rule == "NO_RLS":
        return _gen_no_rls(action)
    if rule == "NO_POLICIES":
        return _gen_no_policies(action)
    if rule == "AUTH_ROLE_AUTHENTICATED":
        return _gen_auth_role_authenticated(action, policy)
    return _make_todo(action, f"No generator available for rule '{rule}'.")


# ---------------------------------------------------------------------------
# Action grouping
# ---------------------------------------------------------------------------


def _group_actions(
    actions: list[RLSPlanAction],
) -> list[list[RLSPlanAction]]:
    """
    Group actions by (priority, table, policy).
    Table-level actions (policy="") are never grouped together.
    Ordering within groups follows input order (already sorted by priority).
    """
    groups: list[list[RLSPlanAction]] = []
    seen: dict[tuple[str, str, str], int] = {}  # key → groups index
    for action in actions:
        if not action.policy:
            # Table-level: always a standalone group
            groups.append([action])
            continue
        key = (action.priority, action.table, action.policy)
        if key in seen:
            groups[seen[key]].append(action)
        else:
            seen[key] = len(groups)
            groups.append([action])
    return groups


# ---------------------------------------------------------------------------
# SQL assembly
# ---------------------------------------------------------------------------

_HEADER_WIDTH = 62


def _assemble_sql(
    blocks: list[SQLBlock],
    path: Path,
    include_medium: bool,
) -> str:
    today = date.today().isoformat()
    auto_count = sum(1 for b in blocks if not b.is_todo)
    todo_count = sum(1 for b in blocks if b.is_todo)
    scope = "CRITICAL + HIGH" + (" + MEDIUM" if include_medium else "")

    header = "\n".join(
        [
            "-- " + "=" * _HEADER_WIDTH,
            "-- AEOS RLS Migration Proposal",
            f"-- Project: {path}",
            f"-- Date:    {today}",
            f"-- Scope:   {scope}",
            f"-- Blocks:  {auto_count} generated, {todo_count} manual TODO(s)",
            "-- WARNING: Review and test before applying.",
            "--          This migration is proposed, NOT applied.",
            "-- " + "=" * _HEADER_WIDTH,
        ]
    )

    lines: list[str] = [header, "", "BEGIN;"]
    current_priority = ""
    for block in blocks:
        if block.priority != current_priority:
            current_priority = block.priority
            sep = (
                "-- -- "
                + current_priority
                + " "
                + "-" * (_HEADER_WIDTH - len(current_priority) - 4)
            )
            lines += ["", sep]
        lines += ["", block.sql]
        if block.warning:
            lines.append(f"-- WARNING: {block.warning}")

    lines += ["", "COMMIT;"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Test plan
# ---------------------------------------------------------------------------


def _build_test_plan(
    actions: list[RLSPlanAction],
) -> list[str]:
    seen: set[tuple[str, str]] = set()
    plan: list[str] = []
    for action in actions:
        key = (action.table, action.risk_type)
        if key not in seen:
            seen.add(key)
            plan.append(f"[{action.table}] {action.recommended_test}")
    return plan


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run_rls_generate(
    path: Path,
    include_medium: bool = False,
) -> RLSGenerateResult:
    """
    Generate a proposed RLS SQL migration from Inspector findings.
    Read-only — no database connection, no .env read, no file modification.
    `applied` is always False — the SQL is proposed only.
    """
    inspect_result = run_rls_inspect(path)
    plan_result = run_rls_plan(path)

    empty_summary = RLSGenerateSummary(
        total_blocks=0,
        auto_generated=0,
        manual_todos=0,
        by_priority={"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0},
        include_medium=include_medium,
    )

    if not plan_result.actions:
        return RLSGenerateResult(
            path=inspect_result.path,
            status=inspect_result.status,
            migrations_scanned=inspect_result.migrations_scanned,
            summary=empty_summary,
            blocks=[],
            generated_sql="-- No RLS actions detected.",
            warnings=[],
            test_plan=[],
            read_only=True,
            applied=False,
        )

    # Policy lookup: (table, policy_name) -> RLSPolicy
    policy_map: dict[tuple[str, str], RLSPolicy] = {
        (p.table, p.name): p for p in inspect_result.policies
    }

    # Project-level context
    tenant_col = _detect_tenant_column(inspect_result.policies)
    has_role_call = _detect_has_role_call(inspect_result.policies)

    # Filter by scope
    target = {"CRITICAL", "HIGH"}
    if include_medium:
        target.add("MEDIUM")
    scoped = [a for a in plan_result.actions if a.priority in target]

    # Group by (priority, table, policy) and generate blocks
    groups = _group_actions(scoped)
    blocks: list[SQLBlock] = []
    for group in groups:
        primary = group[0]
        policy = (
            policy_map.get((primary.table, primary.policy)) if primary.policy else None
        )
        user_id_ok = _has_user_id(inspect_result.policies, primary.table)

        if len(group) == 1:
            block = _dispatch_single(
                primary, policy, tenant_col, has_role_call, user_id_ok
            )
        else:
            block = _gen_combined(group, policy, tenant_col, user_id_ok)
        blocks.append(block)

    # Assemble
    generated_sql = _assemble_sql(blocks, inspect_result.path, include_medium)

    # Collect unique warnings
    warnings: list[str] = []
    for block in blocks:
        if block.warning:
            entry = f"[{block.table}] {block.warning}"
            if entry not in warnings:
                warnings.append(entry)

    # Test plan (deduplicated by table + rule)
    test_plan = _build_test_plan(scoped)

    # Summary
    by_priority: dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0}
    for block in blocks:
        by_priority[block.priority] = by_priority.get(block.priority, 0) + 1

    summary = RLSGenerateSummary(
        total_blocks=len(blocks),
        auto_generated=sum(1 for b in blocks if not b.is_todo),
        manual_todos=sum(1 for b in blocks if b.is_todo),
        by_priority=by_priority,
        include_medium=include_medium,
    )

    return RLSGenerateResult(
        path=inspect_result.path,
        status=inspect_result.status,
        migrations_scanned=inspect_result.migrations_scanned,
        summary=summary,
        blocks=blocks,
        generated_sql=generated_sql,
        warnings=warnings,
        test_plan=test_plan,
        read_only=True,
        applied=False,
    )
