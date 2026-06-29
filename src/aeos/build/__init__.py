"""
AEOS Build Rail — plan and scaffold AEOS-native projects.

Read-only. No project created. No network access. No AI inference.
"""

from aeos.build.planner import (
    BuildPlan,
    VALID_STACKS,
    VALID_TYPES,
    build_plan_to_dict,
    create_build_plan,
    validate_project_type,
    validate_stack,
)

__all__ = [
    "BuildPlan",
    "VALID_STACKS",
    "VALID_TYPES",
    "build_plan_to_dict",
    "create_build_plan",
    "validate_project_type",
    "validate_stack",
]
