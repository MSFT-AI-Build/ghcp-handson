"""Aggregated metadata for tools and MCP servers."""
from __future__ import annotations

from typing import Any

from ..mcp_client import get_mcp_manager


def native_tool_specs() -> list[dict[str, Any]]:
    """Return display specs for tools registered directly with the agent."""
    return [
        {
            "name": "calculate",
            "type": "native",
            "description": "Evaluate basic arithmetic expressions safely.",
            "status": "active",
        },
        {
            "name": "mcp_list_tools",
            "type": "native",
            "description": "List tools exposed by a configured MCP server.",
            "status": "active",
        },
        {
            "name": "mcp_call_tool",
            "type": "native",
            "description": "Invoke a tool on a configured MCP server.",
            "status": "active",
        },
    ]


def build_tools_overview() -> dict[str, Any]:
    """Combined view of native tools and MCP servers for the UI."""
    manager = get_mcp_manager()
    return {
        "tools": native_tool_specs(),
        "mcp_servers": manager.describe_servers(),
    }
