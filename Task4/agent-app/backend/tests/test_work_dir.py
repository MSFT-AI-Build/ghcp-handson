"""Tests for agent work directory initialisation and memory flow."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from app.work_dir import ensure_agent_work_dir, WORK_DIRS_ROOT
from app.mcp_client import (
    MCPClientManager,
    MCPServerError,
    reset_mcp_manager,
    set_mcp_manager,
)
from app.tools.mcp_bridge import mcp_call_tool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

import asyncio


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class MemoryFakeManager(MCPClientManager):
    """Simulates the fileSystem MCP server for read_file / write_file."""

    def __init__(self) -> None:
        super().__init__({"mcpServers": {"fileSystem": {"command": "npx"}}})
        # In-memory filesystem keyed by path
        self._fs: dict[str, str] = {}
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    async def list_tools(self, server: str) -> list[dict[str, Any]]:
        return [
            {"name": "read_file", "description": "Read file"},
            {"name": "write_file", "description": "Write file"},
        ]

    async def call_tool(
        self, server: str, tool: str, arguments: dict[str, Any]
    ) -> Any:
        self._require_known(server)
        self.calls.append((server, tool, arguments))
        if tool == "read_file":
            path = arguments.get("path", "")
            if path not in self._fs:
                raise MCPServerError(f"read_file: file not found: {path}")
            return self._fs[path]
        if tool == "write_file":
            path = arguments.get("path", "")
            content = arguments.get("content", "")
            self._fs[path] = content
            return {"written": len(content)}
        raise MCPServerError(f"unknown tool: {tool}")


@pytest.fixture
def memory_manager():
    mgr = MemoryFakeManager()
    set_mcp_manager(mgr)
    yield mgr
    reset_mcp_manager()


# ---------------------------------------------------------------------------
# Work directory tests
# ---------------------------------------------------------------------------


class TestWorkDir:
    def test_creates_directory(self, tmp_path: Path) -> None:
        agent_dir = ensure_agent_work_dir("test-agent", work_dirs_root=tmp_path)
        assert agent_dir.is_dir()
        assert agent_dir == tmp_path / "test-agent"

    def test_creates_agent_md(self, tmp_path: Path) -> None:
        agent_dir = ensure_agent_work_dir("test-agent", work_dirs_root=tmp_path)
        agent_md = agent_dir / "AGENT.md"
        assert agent_md.exists()
        content = agent_md.read_text(encoding="utf-8")
        assert "test-agent" in content
        assert "Role" in content
        assert "Capabilities" in content

    def test_creates_memory_md(self, tmp_path: Path) -> None:
        agent_dir = ensure_agent_work_dir("test-agent", work_dirs_root=tmp_path)
        memory_md = agent_dir / "MEMORY.md"
        assert memory_md.exists()
        content = memory_md.read_text(encoding="utf-8")
        assert "Memory" in content

    def test_idempotent_does_not_overwrite(self, tmp_path: Path) -> None:
        """Calling ensure_agent_work_dir twice must not overwrite existing files."""
        agent_dir = ensure_agent_work_dir("test-agent", work_dirs_root=tmp_path)
        custom = "# Custom content"
        (agent_dir / "AGENT.md").write_text(custom, encoding="utf-8")
        ensure_agent_work_dir("test-agent", work_dirs_root=tmp_path)
        assert (agent_dir / "AGENT.md").read_text(encoding="utf-8") == custom

    def test_different_agents_isolated(self, tmp_path: Path) -> None:
        dir_a = ensure_agent_work_dir("alpha", work_dirs_root=tmp_path)
        dir_b = ensure_agent_work_dir("beta", work_dirs_root=tmp_path)
        assert dir_a != dir_b
        assert dir_a.parent == dir_b.parent == tmp_path


# ---------------------------------------------------------------------------
# Memory read / write via MCP bridge
# ---------------------------------------------------------------------------


class TestMemoryViaFilesystemMCP:
    """Memory is read/written through the File System MCP server – no native
    load_memory / save_memory tool should exist."""

    def test_no_native_load_save_memory_tools(self) -> None:
        """Ensure there are no native load_memory / save_memory tools."""
        from app.tools import ALL_TOOLS
        names = {getattr(t, "name", None) or getattr(t, "__name__", "") for t in ALL_TOOLS}
        assert "load_memory" not in names
        assert "save_memory" not in names

    def test_read_memory_via_mcp_call_tool(self, memory_manager: MemoryFakeManager) -> None:
        """Agent calls read_file through mcp_call_tool to read MEMORY.md."""
        memory_path = "./agent_work_dirs/supervisor/MEMORY.md"
        memory_manager._fs[memory_path] = "# Memory\n- 사용자 이름: Alice"

        out = _run(
            mcp_call_tool(
                server="fileSystem",
                tool="read_file",
                arguments={"path": memory_path},
            )
        )
        body = json.loads(out)
        assert "Alice" in body["result"]
        assert memory_manager.calls[-1] == (
            "fileSystem",
            "read_file",
            {"path": memory_path},
        )

    def test_write_memory_via_mcp_call_tool(self, memory_manager: MemoryFakeManager) -> None:
        """Agent merges and writes memory via mcp_call_tool write_file."""
        memory_path = "./agent_work_dirs/supervisor/MEMORY.md"
        existing = "# Memory\n- 사용자 이름: Alice\n"
        new_content = existing + "- 선호 언어: Python\n"

        out = _run(
            mcp_call_tool(
                server="fileSystem",
                tool="write_file",
                arguments={"path": memory_path, "content": new_content},
            )
        )
        body = json.loads(out)
        assert body["result"]["written"] == len(new_content)
        assert memory_manager._fs[memory_path] == new_content

    def test_read_write_merge_flow(self, memory_manager: MemoryFakeManager) -> None:
        """Full read → merge → write cycle."""
        memory_path = "./agent_work_dirs/supervisor/MEMORY.md"
        initial = "# Memory\n- 사용자 이름: Bob\n"
        memory_manager._fs[memory_path] = initial

        # Step 1: read
        read_out = _run(
            mcp_call_tool(
                server="fileSystem",
                tool="read_file",
                arguments={"path": memory_path},
            )
        )
        current = json.loads(read_out)["result"]
        assert current == initial

        # Step 2: merge and write
        merged = current + "- 중요 사항: 프로젝트 마감 2026-04-30\n"
        write_out = _run(
            mcp_call_tool(
                server="fileSystem",
                tool="write_file",
                arguments={"path": memory_path, "content": merged},
            )
        )
        assert json.loads(write_out)["result"]["written"] == len(merged)
        assert "마감" in memory_manager._fs[memory_path]

    def test_read_missing_file_raises_mcp_error(
        self, memory_manager: MemoryFakeManager
    ) -> None:
        """Reading a non-existent MEMORY.md returns an error JSON (MCPServerError)."""
        out = _run(
            mcp_call_tool(
                server="fileSystem",
                tool="read_file",
                arguments={"path": "./agent_work_dirs/supervisor/MEMORY.md"},
            )
        )
        body = json.loads(out)
        assert "error" in body


# ---------------------------------------------------------------------------
# Supervisor agent creates its work directory on init
# ---------------------------------------------------------------------------


class TestSupervisorAgentWorkDir:
    def test_get_supervisor_agent_creates_work_dir(self, tmp_path: Path) -> None:
        """get_supervisor_agent() must initialise the work directory."""
        from app import agents
        from app.agents import reset_supervisor_agent

        reset_supervisor_agent()
        with patch.object(agents, "WORK_DIRS_ROOT", tmp_path):
            with patch("app.agents.ensure_agent_work_dir") as mock_ensure:
                # Prevent actual Agent construction from calling Azure
                with patch("app.agents.OpenAIChatClient"):
                    with patch("app.agents.Agent"):
                        agents.get_supervisor_agent()
                        mock_ensure.assert_called_once_with(agents.AGENT_ID)
        reset_supervisor_agent()

    def test_memory_instructions_in_system_prompt(self) -> None:
        from app.agents import SUPERVISOR_INSTRUCTIONS, AGENT_ID
        assert "MEMORY.md" in SUPERVISOR_INSTRUCTIONS
        assert "read_file" in SUPERVISOR_INSTRUCTIONS
        assert "write_file" in SUPERVISOR_INSTRUCTIONS
        assert AGENT_ID in SUPERVISOR_INSTRUCTIONS
