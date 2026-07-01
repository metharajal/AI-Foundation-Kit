"""AEOS UI — static dashboard and workspace generation."""

from aeos.ui.dashboard import DashboardData, load_dashboard_data, render_dashboard
from aeos.ui.workspace import (
    ProductionReadiness,
    RecoveryProgress,
    WorkspaceData,
    load_workspace_data,
    render_workspace,
)

__all__ = [
    "DashboardData",
    "ProductionReadiness",
    "RecoveryProgress",
    "WorkspaceData",
    "load_dashboard_data",
    "load_workspace_data",
    "render_dashboard",
    "render_workspace",
]
