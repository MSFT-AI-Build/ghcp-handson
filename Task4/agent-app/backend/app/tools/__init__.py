"""Tool components registered with the supervisor agent."""
from __future__ import annotations

from .mcp_bridge import mcp_call_tool, mcp_list_tools
from .native import calculate
from .registry import build_tools_overview, native_tool_specs

ALL_TOOLS = [calculate, mcp_list_tools, mcp_call_tool]

__all__ = [
    "ALL_TOOLS",
    "calculate",
    "mcp_call_tool",
    "mcp_list_tools",
    "build_tools_overview",
    "native_tool_specs",
]
