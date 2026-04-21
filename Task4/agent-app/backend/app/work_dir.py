"""Agent work directory management.

Each agent gets an isolated directory under ``./agent_work_dirs/{agent_id}/``
containing:

* ``AGENT.md`` – role, description, capabilities (written once at init)
* ``MEMORY.md`` – conversational memory, updated by the agent at runtime
  via the File System MCP server (``mcp_call_tool``).
"""
from __future__ import annotations

import logging
import textwrap
from pathlib import Path

logger = logging.getLogger(__name__)

#: Root directory for all agent work directories, relative to the CWD of the
#: backend process (i.e. ``agent-app/backend/``).
WORK_DIRS_ROOT = Path("agent_work_dirs")


def ensure_agent_work_dir(agent_id: str, work_dirs_root: Path | None = None) -> Path:
    """Create ``{root}/{agent_id}/`` with default AGENT.md and MEMORY.md.

    Idempotent – existing files are not overwritten.

    Returns the agent's work directory path.
    """
    root = work_dirs_root if work_dirs_root is not None else WORK_DIRS_ROOT
    agent_dir = root / agent_id
    agent_dir.mkdir(parents=True, exist_ok=True)

    _init_agent_md(agent_dir, agent_id)
    _init_memory_md(agent_dir)

    logger.debug("Agent work directory ready: %s", agent_dir)
    return agent_dir


def _init_agent_md(agent_dir: Path, agent_id: str) -> None:
    path = agent_dir / "AGENT.md"
    if path.exists():
        return
    path.write_text(
        textwrap.dedent(f"""\
        # Agent: {agent_id}

        ## Role
        Supervisor Agent – orchestrates tools and MCP servers to fulfil user requests.

        ## Capabilities
        - Native tools: `calculate`
        - MCP bridge tools: `mcp_list_tools`, `mcp_call_tool`
        - MCP servers: fileSystem, notion, braveSearch

        ## Memory
        Use `MEMORY.md` in this directory to persist important information across
        conversations (read via `mcp_call_tool` with server=fileSystem, tool=read_file).
        """),
        encoding="utf-8",
    )


def _init_memory_md(agent_dir: Path) -> None:
    path = agent_dir / "MEMORY.md"
    if path.exists():
        return
    path.write_text(
        textwrap.dedent("""\
        # Memory

        <!-- 에이전트가 대화 중 중요한 정보를 이곳에 기록합니다. -->
        <!-- 최신 항목이 위에 오도록 날짜·내용을 추가하세요.       -->
        """),
        encoding="utf-8",
    )
