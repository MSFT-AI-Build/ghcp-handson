"""Tool components registered with agents.

The Supervisor exposes only delegation tools. Workers expose Native tools
plus the MCP bridge tools so they can use external services.
"""
from __future__ import annotations

from .delegation import (
    SUPERVISOR_DELEGATION_TOOLS,
    cancel_worker,
    check_workers,
    delegate_task,
    get_active_worker_manager,
    reset_active_worker_manager,
    set_active_worker_manager,
)
from .mcp_bridge import mcp_call_tool, mcp_list_tools
from .native import calculate
from .registry import build_tools_overview, native_tool_specs

# Workers do the actual work; they have native + MCP bridge tools.
WORKER_TOOLS = [calculate, mcp_list_tools, mcp_call_tool]

# Supervisor cannot use MCP servers directly; it must delegate.
SUPERVISOR_TOOLS = list(SUPERVISOR_DELEGATION_TOOLS)

# Backwards-compatible alias used by existing tests/callers expecting the
# full set of *worker* tools (registry overview, memory tests, etc.).
ALL_TOOLS = WORKER_TOOLS

__all__ = [
    "ALL_TOOLS",
    "SUPERVISOR_TOOLS",
    "WORKER_TOOLS",
    "calculate",
    "cancel_worker",
    "check_workers",
    "delegate_task",
    "get_active_worker_manager",
    "mcp_call_tool",
    "mcp_list_tools",
    "reset_active_worker_manager",
    "set_active_worker_manager",
    "build_tools_overview",
    "native_tool_specs",
]

