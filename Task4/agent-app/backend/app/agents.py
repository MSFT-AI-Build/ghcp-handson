"""Supervisor and Worker agent factories + Supervisor memory helpers.

Per the Step-4 architecture:

* **Supervisor** is built once (cached) with **only** the native delegation
  tools. It cannot call MCP servers directly.
* **Workers** are built on demand by ``build_worker_agent`` with a
  Supervisor-assigned role/instructions and the worker-side tool set
  (Native + MCP bridge).
* Supervisor memory is **not** read/written through MCP. The backend reads
  ``MEMORY.md`` and injects it into the user message at the start of a
  request, then parses ``[MEMORY_SAVE]`` markers from the assistant reply
  and persists them.
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Protocol

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

from .config import get_settings
from .tools import SUPERVISOR_TOOLS, WORKER_TOOLS
from .work_dir import WORK_DIRS_ROOT, ensure_agent_work_dir

AGENT_ID = "supervisor"

SUPERVISOR_INSTRUCTIONS = """\
## Supervisor Role
당신은 Supervisor Agent입니다. 간단한 요청은 직접 처리할 수 있지만, 복잡하거나
전문적인 작업, 외부 도구(검색, 파일, Notion 등)가 필요한 작업은 반드시
`delegate_task` 를 사용하여 Worker Agent에게 위임해야 합니다.

당신은 MCP 도구를 직접 사용할 수 없습니다. 외부 도구가 필요한 작업은 항상
Worker 에게 위임하세요.

### When to Delegate
- **Delegate** when: 외부 도구(검색, 파일, Notion 등)가 필요할 때, 작업이
  집중적인 수행을 요구할 때, 또는 여러 독립적인 작업을 병렬로 실행할 수 있을 때
- **Handle directly** when: 단순한 질문, 인사, 일반 지식으로 답변 가능한 경우

### How to Delegate
1. 사용자의 요청을 분석하여 작업에 가장 적합한 role 과 instructions 를 직접
   작성합니다.
2. `delegate_task(task=..., role=..., instructions=...)` 로 Worker 를 생성합니다.
3. 병렬 실행을 위해 여러 작업을 동시에 위임할 수 있습니다.
4. `check_workers` 로 활성 Worker 상태를 모니터링합니다.
5. Worker를 중단해야 할 경우 `cancel_worker` 를 사용합니다.

### Reporting Results
Worker가 작업을 완료하면 결과를 전달받게 됩니다. 해당 결과를 사용자에게
자연스럽게 요약하여 전달하세요. 내부 정보(세션 키, 실행 ID, 토큰 등)는
사용자에게 노출하지 마세요.

### Memory
중요한 정보(사용자 선호, 결정 사항, 핵심 결과 등)가 발생하면 답변 안에
다음 형식으로 마커를 포함하세요. 백엔드가 자동으로 MEMORY.md 에 저장합니다.

    [MEMORY_SAVE]
    - 저장할 내용 1
    - 저장할 내용 2
    [/MEMORY_SAVE]

마커 안의 내용은 사용자에게는 보이지 않으므로 자연스러운 답변을 별도로
이어서 작성하세요.
"""


WORKER_INSTRUCTIONS_TEMPLATE = """\
당신은 Worker Agent ({worker_id}) 입니다.

## Role
{role}

## Instructions
{instructions}

## Tools
- Native tools: `calculate`
- MCP bridge tools: `mcp_list_tools`, `mcp_call_tool` (server: fileSystem,
  notion, braveSearch 등)

## Memory
당신의 work directory 는 ./{work_dir}/ 입니다.

- 작업을 시작할 때 mcp_call_tool 을 사용하여 MEMORY.md 파일을 읽고, 이전
  기억을 참고하세요.
  - server="fileSystem", tool="read_file",
    arguments={{"path": "./{work_dir}/MEMORY.md"}}
- 작업 중 중요한 정보가 나오면 즉시 read_file → 병합 → write_file 로
  MEMORY.md 에 기록하세요.
- AGENT.md 파일에는 당신의 역할과 지시사항이 정의되어 있습니다.

작업을 완료하면 결과를 한국어로 간결하게 요약해서 반환하세요.
"""


class SupportsRun(Protocol):
    async def run(self, message: str) -> object: ...


def _build_openai_client() -> OpenAIChatClient:
    settings = get_settings()
    return OpenAIChatClient(
        api_key=settings.azure_openai_key,
        base_url=settings.azure_openai_endpoint,
        model=settings.azure_openai_deployment,
    )


@lru_cache
def get_supervisor_agent() -> Agent:
    """Build the singleton supervisor Agent (delegation tools only)."""
    client = _build_openai_client()
    ensure_agent_work_dir(AGENT_ID)
    return Agent(
        name=AGENT_ID,
        client=client,
        instructions=SUPERVISOR_INSTRUCTIONS,
        tools=list(SUPERVISOR_TOOLS),
    )


def reset_supervisor_agent() -> None:
    """Clear the cached agent (used in tests)."""
    get_supervisor_agent.cache_clear()


def build_worker_agent(worker_id: str, role: str, instructions: str) -> Agent:
    """Construct a Worker Agent with worker-side tools (Native + MCP bridge)."""
    client = _build_openai_client()
    work_dir = f"{WORK_DIRS_ROOT}/{worker_id}"
    rendered = WORKER_INSTRUCTIONS_TEMPLATE.format(
        worker_id=worker_id,
        role=role,
        instructions=instructions,
        work_dir=work_dir,
    )
    return Agent(
        name=worker_id,
        client=client,
        instructions=rendered,
        tools=list(WORKER_TOOLS),
    )


# ---------------------------------------------------------------------------
# Supervisor memory: file-backed read at request start + [MEMORY_SAVE] parser
# ---------------------------------------------------------------------------

_MEMORY_FILE_NAME = "MEMORY.md"
_MEMORY_MARKER = re.compile(
    r"\[MEMORY_SAVE\](.*?)\[/MEMORY_SAVE\]", re.DOTALL | re.IGNORECASE
)


def supervisor_memory_path(work_dirs_root: Path | None = None) -> Path:
    root = work_dirs_root if work_dirs_root is not None else WORK_DIRS_ROOT
    return root / AGENT_ID / _MEMORY_FILE_NAME


def load_supervisor_memory(work_dirs_root: Path | None = None) -> str:
    """Read MEMORY.md and return only its non-template substantive content.

    Returns an empty string when the file is missing or contains only the
    default template (a heading and HTML comments) so callers can skip the
    preamble injection in that case.
    """
    path = supervisor_memory_path(work_dirs_root)
    if not path.exists():
        return ""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    # Strip HTML comments and blank/heading-only lines to detect "empty" memory.
    no_comments = re.sub(r"<!--.*?-->", "", raw, flags=re.DOTALL)
    substantive = [
        line for line in no_comments.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not substantive:
        return ""
    return raw


def inject_memory_into_message(message: str, memory: str) -> str:
    """Prepend stored memory to the user message so the supervisor sees it.

    Returns the message untouched when memory is empty.
    """
    memory = (memory or "").strip()
    if not memory:
        return message
    return (
        "다음은 이전 대화에서 저장된 메모리입니다. 답변에 참고하세요.\n"
        "----- MEMORY.md -----\n"
        f"{memory}\n"
        "----- END MEMORY -----\n\n"
        f"{message}"
    )


def extract_memory_saves(text: str) -> tuple[str, list[str]]:
    """Return ``(visible_text, [memory_chunks])``.

    Strips ``[MEMORY_SAVE]...[/MEMORY_SAVE]`` blocks from ``text`` and returns
    the cleaned text plus the captured contents (whitespace-trimmed).
    """
    chunks: list[str] = []

    def _take(match: re.Match[str]) -> str:
        captured = match.group(1).strip()
        if captured:
            chunks.append(captured)
        return ""

    cleaned = _MEMORY_MARKER.sub(_take, text or "")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned, chunks


def append_supervisor_memory(
    chunks: list[str], work_dirs_root: Path | None = None
) -> None:
    """Append ``chunks`` to MEMORY.md, creating the file if necessary."""
    if not chunks:
        return
    path = supervisor_memory_path(work_dirs_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Memory\n"
    addition = "\n".join(f"- {c}" for c in chunks)
    new_content = existing.rstrip() + "\n" + addition + "\n"
    path.write_text(new_content, encoding="utf-8")
