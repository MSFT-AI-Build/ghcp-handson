"""Supervisor agent factory."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Protocol

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

from .config import get_settings
from .tools import ALL_TOOLS
from .work_dir import ensure_agent_work_dir, WORK_DIRS_ROOT

AGENT_ID = "supervisor"

_MEMORY_INSTRUCTIONS = f"""\

## Memory
당신의 work directory 는 ./{WORK_DIRS_ROOT}/{AGENT_ID}/ 입니다.
- 대화를 시작할 때 mcp_call_tool 을 사용하여 MEMORY.md 파일을 읽고, 이전 기억을 참고하세요.
  - server="fileSystem", tool="read_file", arguments={{"path": "./{WORK_DIRS_ROOT}/{AGENT_ID}/MEMORY.md"}}
- 대화 중 중요한 정보(사용자 선호, 결정 사항, 핵심 결과 등)가 나오면 즉시 MEMORY.md 에 저장하세요.
  - 먼저 기존 MEMORY.md 를 read_file 로 읽어 내용을 확인한 뒤,
  - 새 내용을 병합하여 write_file 로 덮어씁니다.
  - 대화 종료까지 기다리지 말고, 중요한 정보가 나오는 시점에 바로 기록하세요.
- AGENT.md 파일에는 당신의 역할과 능력이 정의되어 있습니다. 필요 시 참고하세요.
  - server="fileSystem", tool="read_file", arguments={{"path": "./{WORK_DIRS_ROOT}/{AGENT_ID}/AGENT.md"}}
"""

SUPERVISOR_INSTRUCTIONS = (
    "You are the Supervisor Agent. Understand the user's request and "
    "answer concisely. Use the registered tools when helpful: call the "
    "native `calculate` tool for arithmetic, and use the MCP bridge "
    "tools `mcp_list_tools` then `mcp_call_tool` to interact with "
    "configured MCP servers (notion, fileSystem, braveSearch)."
    + _MEMORY_INSTRUCTIONS
)


class SupportsRun(Protocol):
    async def run(self, message: str) -> object: ...


@lru_cache
def get_supervisor_agent() -> Agent:
    """Build the singleton supervisor Agent backed by Azure OpenAI."""
    settings = get_settings()
    client = OpenAIChatClient(
        api_key=settings.azure_openai_key,
        base_url=settings.azure_openai_endpoint,
        model=settings.azure_openai_deployment,
    )
    ensure_agent_work_dir(AGENT_ID)
    return Agent(
        name=AGENT_ID,
        client=client,
        instructions=SUPERVISOR_INSTRUCTIONS,
        tools=list(ALL_TOOLS),
    )


def reset_supervisor_agent() -> None:
    """Clear the cached agent (used in tests)."""
    get_supervisor_agent.cache_clear()
