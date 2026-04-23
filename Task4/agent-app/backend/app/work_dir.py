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


def ensure_agent_work_dir(
    agent_id: str,
    work_dirs_root: Path | None = None,
    *,
    role: str | None = None,
    instructions: str | None = None,
    capabilities: list[str] | None = None,
    overwrite_agent_md: bool = False,
) -> Path:
    """Create ``{root}/{agent_id}/`` with AGENT.md and MEMORY.md.

    Idempotent – existing files are not overwritten unless
    ``overwrite_agent_md=True`` is passed (used when a Worker is (re)assigned a
    new role/instructions by the Supervisor).

    Returns the agent's work directory path.
    """
    root = work_dirs_root if work_dirs_root is not None else WORK_DIRS_ROOT
    agent_dir = root / agent_id
    agent_dir.mkdir(parents=True, exist_ok=True)

    _init_agent_md(
        agent_dir,
        agent_id,
        role=role,
        instructions=instructions,
        capabilities=capabilities,
        overwrite=overwrite_agent_md,
    )
    _init_memory_md(agent_dir)

    logger.debug("Agent work directory ready: %s", agent_dir)
    return agent_dir


def _init_agent_md(
    agent_dir: Path,
    agent_id: str,
    *,
    role: str | None = None,
    instructions: str | None = None,
    capabilities: list[str] | None = None,
    overwrite: bool = False,
) -> None:
    path = agent_dir / "AGENT.md"
    if path.exists() and not overwrite:
        return
    if role is None and instructions is None and capabilities is None:
        # Default supervisor template (back-compat).
        body = textwrap.dedent(f"""\
            # Agent: {agent_id}

            ## Role
            Supervisor Agent – orchestrates tools and delegates work to Worker
            Agents to fulfil user requests.

            ## Capabilities
            - Native delegation tools: `delegate_task`, `check_workers`, `cancel_worker`

            ## Memory
            Use `MEMORY.md` in this directory to persist important information
            across conversations.
            """)
    else:
        cap_lines = "\n".join(f"- {c}" for c in (capabilities or [])) or "- (none)"
        body = textwrap.dedent(f"""\
            # Agent: {agent_id}

            ## Role
            {role or "(unspecified)"}

            ## Instructions
            {instructions or "(none)"}

            ## Capabilities
            {cap_lines}

            ## Memory
            Use `MEMORY.md` in this directory to persist important information
            via the File System MCP server.
            """)
    path.write_text(body, encoding="utf-8")


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
