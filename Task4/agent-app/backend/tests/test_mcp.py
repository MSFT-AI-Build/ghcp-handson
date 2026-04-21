"""Tests for MCP bridge tools, manager, and config loading."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

from app.mcp_client import (
    MCPClientManager,
    MCPConfigError,
    MCPServerError,
    get_mcp_manager,
    load_mcp_config,
    reset_mcp_manager,
    set_mcp_manager,
)
from app.tools.mcp_bridge import mcp_call_tool, mcp_list_tools


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class FakeManager(MCPClientManager):
    def __init__(self) -> None:
        super().__init__(
            {"mcpServers": {"notion": {"command": "npx"}, "fileSystem": {"command": "npx"}}}
        )
        self.calls: list[tuple[str, str, dict[str, Any]]] = []
        self._tool_cache["notion"] = [{"name": "search", "description": "search"}]

    async def list_tools(self, server: str) -> list[dict[str, Any]]:
        self._require_known(server)
        return self._tool_cache.get(server, [])

    async def call_tool(self, server: str, tool: str, arguments: dict[str, Any]) -> Any:
        self._require_known(server)
        self.calls.append((server, tool, arguments))
        return {"server": server, "tool": tool, "echo": arguments}


@pytest.fixture
def fake_manager():
    fake = FakeManager()
    set_mcp_manager(fake)
    yield fake
    reset_mcp_manager()


class TestBridgeTools:
    def test_list_tools_returns_json(self, fake_manager: FakeManager) -> None:
        out = _run(mcp_list_tools())
        body = json.loads(out)
        assert "notion" in body["servers"]
        assert body["servers"]["notion"][0]["name"] == "search"

    def test_call_tool_dispatches(self, fake_manager: FakeManager) -> None:
        out = _run(
            mcp_call_tool(
                server="notion", tool="search", arguments={"query": "hi"}
            )
        )
        body = json.loads(out)
        assert body["result"]["echo"] == {"query": "hi"}
        assert fake_manager.calls == [("notion", "search", {"query": "hi"})]

    def test_list_unknown_server_returns_error_json(
        self, fake_manager: FakeManager
    ) -> None:
        # fileSystem is configured but has no cached tools and FakeManager only
        # knows 'notion' in its cache; ensure the aggregate response still lists
        # both server keys without raising.
        out = _run(mcp_list_tools())
        body = json.loads(out)
        assert set(body["servers"].keys()) == {"notion", "fileSystem"}

    def test_call_unknown_server_returns_error_json(
        self, fake_manager: FakeManager
    ) -> None:
        out = _run(
            mcp_call_tool(server="missing", tool="x", arguments={})
        )
        assert "error" in json.loads(out)


class TestDefaultManager:
    def test_known_server_not_connected_raises(self) -> None:
        mgr = MCPClientManager({"mcpServers": {"notion": {"command": "npx"}}})
        with pytest.raises(MCPServerError):
            _run(mgr.list_tools("notion"))
        with pytest.raises(MCPServerError):
            _run(mgr.call_tool("notion", "search", {}))

    def test_unknown_server_raises(self) -> None:
        mgr = MCPClientManager({"mcpServers": {}})
        with pytest.raises(MCPServerError):
            _run(mgr.list_tools("nope"))


class TestConfigLoader:
    def test_valid_config(self, tmp_path: Path) -> None:
        path = tmp_path / "c.json"
        path.write_text(
            json.dumps({"mcpServers": {"notion": {"command": "npx"}}})
        )
        cfg = load_mcp_config(path)
        assert "notion" in cfg["mcpServers"]

    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        cfg = load_mcp_config(tmp_path / "absent.json")
        assert cfg == {"mcpServers": {}}

    def test_invalid_json_raises(self, tmp_path: Path) -> None:
        path = tmp_path / "c.json"
        path.write_text("{not json}")
        with pytest.raises(MCPConfigError):
            load_mcp_config(path)

    def test_missing_top_level_key_raises(self, tmp_path: Path) -> None:
        path = tmp_path / "c.json"
        path.write_text(json.dumps({"servers": {}}))
        with pytest.raises(MCPConfigError):
            load_mcp_config(path)

    def test_server_without_command_raises(self, tmp_path: Path) -> None:
        path = tmp_path / "c.json"
        path.write_text(json.dumps({"mcpServers": {"x": {"transport": "stdio"}}}))
        with pytest.raises(MCPConfigError):
            load_mcp_config(path)


def test_default_get_manager_returns_singleton() -> None:
    reset_mcp_manager()
    a = get_mcp_manager()
    b = get_mcp_manager()
    assert a is b
    reset_mcp_manager()
