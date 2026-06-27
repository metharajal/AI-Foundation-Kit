"""
Supabase RLS Plan Advisor — transforms RLS Inspector findings into a
prioritized hardening plan.

Read-only. No network access. No secret reads. No file modification.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from aeos.providers.supabase.rls.inspector import RLSFinding, run_rls_inspect

# ---------------------------------------------------------------------------
# Priority constants
# ---------------------------------------------------------------------------

_PRIORITY_ORDER: dict[str, int] = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

# Rule → base priority (SELECT_TOO_PERMISSIVE upgraded to CRITICAL when ERROR)
_RULE_PRIORITY: dict[str, str] = {
    "NO_RLS": "CRITICAL",
    "SENSITIVE_TABLE_OPEN_SELECT": "CRITICAL",
    "SELECT_TOO_PERMISSIVE": "MEDIUM",  # overridden below if severity == ERROR
    "NO_POLICIES": "HIGH",
    "INSERT_NO_WITH_CHECK": "HIGH",
    "UPDATE_NO_WITH_CHECK": "HIGH",
    "MISSING_TENANT_SCOPE": "HIGH",
    "AUTH_ROLE_AUTHENTICATED": "MEDIUM",
    "NO_DELETE_POLICY": "MEDIUM",
}

# ---------------------------------------------------------------------------
# Impact and test templates per rule
# ---------------------------------------------------------------------------

_FUNCTIONAL_IMPACT: dict[str, str] = {
    "NO_RLS": (
        "All rows are accessible to any database role — no row-level isolation."
        " Data from all users and tenants is fully exposed."
    ),
    "NO_POLICIES": (
        "RLS is enabled but blocks all access — legitimate users cannot read"
        " or write. The table is effectively locked down."
    ),
    "SELECT_TOO_PERMISSIVE": (
        "All authenticated users can read every row in the table."
        " Cross-tenant and cross-user data leakage is possible."
    ),
    "SENSITIVE_TABLE_OPEN_SELECT": (
        "Sensitive fields (PII, financial records, personnel data) are exposed"
        " to all authenticated users regardless of commune or role."
    ),
    "INSERT_NO_WITH_CHECK": (
        "An authenticated user can insert rows with any user_id or commune_id,"
        " bypassing ownership validation at write time."
    ),
    "UPDATE_NO_WITH_CHECK": (
        "After a permitted write, an attacker can escalate row ownership by"
        " updating user_id or commune_id to any value."
    ),
    "MISSING_TENANT_SCOPE": (
        "An agent or user from commune A can write data into commune B's dataset"
        " — cross-tenant data corruption is possible."
    ),
    "AUTH_ROLE_AUTHENTICATED": (
        "Any logged-in user passes this policy regardless of their commune"
        " or assigned role — isolation is not enforced."
    ),
    "NO_DELETE_POLICY": (
        "Users cannot delete their own submissions. Administrators and moderators"
        " cannot remove abusive or erroneous content."
    ),
}

_RECOMMENDED_TEST: dict[str, str] = {
    "NO_RLS": (
        "Attempt SELECT as an unauthenticated user — all rows should be blocked."
        " Attempt SELECT as user A — rows from user B should not appear."
    ),
    "NO_POLICIES": (
        "Attempt SELECT as an authenticated user after adding policies"
        " — they should see only their own rows."
    ),
    "SELECT_TOO_PERMISSIVE": (
        "Query the table as user A — rows created by user B from another commune"
        " should not be returned."
        " Verify SELECT is intentional for public data only."
    ),
    "SENSITIVE_TABLE_OPEN_SELECT": (
        "Query the table as a citizen user — phone, email, and salary fields"
        " from other users should not be returned."
    ),
    "INSERT_NO_WITH_CHECK": (
        "Insert a row as user A with user_id set to user B's ID"
        " — the INSERT should be rejected by the WITH CHECK constraint."
    ),
    "UPDATE_NO_WITH_CHECK": (
        "Update a row's user_id to another user's ID as user A"
        " — the UPDATE should be rejected by the WITH CHECK constraint."
    ),
    "MISSING_TENANT_SCOPE": (
        "Insert or update a row with commune_id set to a different commune's ID"
        " — the operation should be rejected by the WITH CHECK constraint."
    ),
    "AUTH_ROLE_AUTHENTICATED": (
        "Attempt access as a user with no specific role assigned"
        " — the request should be denied."
        " Verify the policy is not too broad."
    ),
    "NO_DELETE_POLICY": (
        "Attempt DELETE as the row owner — should succeed after fix."
        " Attempt DELETE as a different user — should be denied."
        " Attempt DELETE as an agent/admin — should succeed for moderation."
    ),
}

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class RLSPlanAction:
    order: int
    priority: str  # CRITICAL | HIGH | MEDIUM | LOW
    table: str
    policy: str  # policy name, or "" for table-level issues
    risk_type: str  # rule name from inspector
    severity: str  # ERROR | WARNING
    problem: str
    fix: str
    functional_impact: str
    recommended_test: str
    source_file: str


@dataclass
class RLSPlanSummary:
    total_actions: int
    by_priority: dict[str, int]
    riskiest_tables: list[str]
    application_order: list[str]


@dataclass
class RLSPlanResult:
    path: Path
    status: str  # OK | WARNING | ERROR
    migrations_scanned: int
    summary: RLSPlanSummary
    actions: list[RLSPlanAction] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    read_only: bool = True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_POLICY_NAME_RE = re.compile(r"Policy '([^']+)'")


def _extract_policy_name(message: str) -> str:
    m = _POLICY_NAME_RE.search(message)
    return m.group(1) if m else ""


def _finding_priority(finding: RLSFinding) -> str:
    base = _RULE_PRIORITY.get(finding.rule, "LOW")
    if finding.rule == "SELECT_TOO_PERMISSIVE" and finding.severity == "ERROR":
        return "CRITICAL"
    return base


def _finding_to_action(finding: RLSFinding, order: int) -> RLSPlanAction:
    priority = _finding_priority(finding)
    impact = _FUNCTIONAL_IMPACT.get(
        finding.rule,
        "Risk requires review — check policy intent before deploying.",
    )
    test = _RECOMMENDED_TEST.get(
        finding.rule,
        "Verify access control manually for this table and operation.",
    )
    return RLSPlanAction(
        order=order,
        priority=priority,
        table=finding.table,
        policy=_extract_policy_name(finding.message),
        risk_type=finding.rule,
        severity=finding.severity,
        problem=finding.message,
        fix=finding.recommendation,
        functional_impact=impact,
        recommended_test=test,
        source_file=finding.source_file,
    )


def _build_summary(actions: list[RLSPlanAction]) -> RLSPlanSummary:
    by_priority: dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    table_counts: dict[str, int] = {}
    for action in actions:
        by_priority[action.priority] = by_priority.get(action.priority, 0) + 1
        table_counts[action.table] = table_counts.get(action.table, 0) + 1

    riskiest = sorted(table_counts, key=lambda t: -table_counts[t])[:5]
    app_order = [
        p for p in ("CRITICAL", "HIGH", "MEDIUM", "LOW") if by_priority.get(p, 0) > 0
    ]
    return RLSPlanSummary(
        total_actions=len(actions),
        by_priority=by_priority,
        riskiest_tables=riskiest,
        application_order=app_order,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run_rls_plan(path: Path) -> RLSPlanResult:
    """
    Build a prioritized RLS hardening plan from Inspector findings.
    Read-only — no database connection, no .env read, no file modification.
    """
    inspect_result = run_rls_inspect(path)

    empty_summary = RLSPlanSummary(
        total_actions=0,
        by_priority={"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
        riskiest_tables=[],
        application_order=[],
    )

    if not inspect_result.findings:
        return RLSPlanResult(
            path=inspect_result.path,
            status=inspect_result.status,
            migrations_scanned=inspect_result.migrations_scanned,
            summary=empty_summary,
            actions=[],
            recommendations=inspect_result.recommendations,
            read_only=True,
        )

    sorted_findings = sorted(
        inspect_result.findings,
        key=lambda f: (
            _PRIORITY_ORDER.get(_finding_priority(f), 9),
            f.table,
            f.rule,
        ),
    )

    actions = [
        _finding_to_action(finding, order=i + 1)
        for i, finding in enumerate(sorted_findings)
    ]

    summary = _build_summary(actions)

    return RLSPlanResult(
        path=inspect_result.path,
        status=inspect_result.status,
        migrations_scanned=inspect_result.migrations_scanned,
        summary=summary,
        actions=actions,
        recommendations=inspect_result.recommendations,
        read_only=True,
    )
