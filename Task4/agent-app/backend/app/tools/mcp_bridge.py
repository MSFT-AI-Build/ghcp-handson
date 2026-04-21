"""MCP bridge tools registered with the agent."""
from __future__ import annotations

import json
from typing import Annotated, Any

from agent_framework import tool

from ..mcp_client import MCPServerError, get_mcp_manager


@tool(
    name="mcp_list_tools",
    description=(
        "List the tools exposed by every configured MCP server. "
        "Returns a JSON string mapping each server name to its tool list "
        "(name/description/input schema)."
    ),
)
async def mcp_list_tools() -> str:
    manager = get_mcp_manager()
    overview: dict[str, Any] = {}
    for name in manager.server_names:
        try:
            overview[name] = await manager.list_tools(name)
        except MCPServerError as exc:
            overview[name] = {"error": str(exc)}
    return json.dumps({"servers": overview}, ensure_ascii=False)


@tool(
    name="mcp_call_tool",
    description=(
        "Invoke a specific tool on a configured MCP server. "
        "Provide arguments matching the tool's input schema."
    ),
)
async def mcp_call_tool(
    server: Annotated[str, "Configured MCP server name."],
    tool: Annotated[str, "Tool name as returned by mcp_list_tools."],
    arguments: Annotated[
        dict[str, Any] | None, "Arguments to pass to the MCP tool (JSON object)."
    ] = None,
) -> str:
    manager = get_mcp_manager()
    try:
        result = await manager.call_tool(server, tool, arguments or {})
    except MCPServerError as exc:
        return json.dumps({"error": str(exc)})
    return json.dumps(
        {"server": server, "tool": tool, "result": result}, ensure_ascii=False
    )
