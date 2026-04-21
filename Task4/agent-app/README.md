# Agent System

Supervisor 에이전트(FastAPI + agent-framework) 백엔드와 React + Vite 프론트엔드로 구성된 데모.

## 디렉터리

- `backend/` — FastAPI 앱, 에이전트, 도구(Native + MCP Bridge), 테스트
- `frontend/` — React + TS + Vite UI (Chat / Agents / Settings)

## 실행

### Backend
```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 필요한 값 채우기
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 테스트

```bash
# Backend (Azure OpenAI·MCP 서버 없이 실행 가능)
cd backend && pytest -q

# Frontend
cd frontend && npm test -- --run
```

테스트는 LLM(Azure OpenAI) 및 MCP 서버를 모두 **목(mock)** 으로 대체하므로 외부 서비스나 실제 MCP 서버 프로세스 없이 로컬에서 실행 가능합니다.
파일시스템 관련 테스트는 `pytest` 내장 `tmp_path` 픽스처를 사용해 임시 디렉터리에서 동작하므로 실제 `agent_work_dirs/` 디렉터리가 없어도 통과합니다.

## Configuration

- `backend/.env` — Azure OpenAI 등 자격 증명 (`.env.example` 참고)
- `backend/mcp_servers/mcp_config.json` — MCP 서버 정의. 기본 항목:
  - `notion` (`@notionhq/notion-mcp-server`, stdio) — `NOTION_TOKEN` 필요
  - `fileSystem` (`@modelcontextprotocol/server-filesystem`, stdio)
  - `braveSearch` (`@brave/brave-search-mcp-server`, stdio) — `BRAVE_API_KEY` 필요

## 도구

- **Native Tool**: `calculate` (안전한 산술 평가)
- **MCP Bridge Tool**: `mcp_list_tools`, `mcp_call_tool` — 위 MCP 서버에 대해 `tools/list`·`tools/call` 중계

## Agent Memory (File System MCP)

에이전트는 대화 중 중요한 정보를 **File System MCP 서버**를 통해 파일에 직접 기록합니다.
별도의 `load_memory`/`save_memory` Native Tool 은 존재하지 않습니다.

### Work Directory 구조

```
backend/
└── agent_work_dirs/
    └── supervisor/
        ├── AGENT.md    ← 에이전트 역할·능력 정의 (기동 시 자동 생성)
        └── MEMORY.md   ← 대화 중 에이전트가 직접 기록·갱신
```

`agent_work_dirs/` 는 `uvicorn app.main:app` 실행 시 (`backend/` 디렉터리를 CWD로) 자동 생성됩니다.

### Memory 흐름

```
1) 대화 시작: mcp_call_tool(server="fileSystem", tool="read_file",
                             arguments={"path": "./agent_work_dirs/supervisor/MEMORY.md"})
   → 이전 기억 로드

2) 중요 정보 발생 시:
   read_file  → 기존 내용 읽기
   write_file → 새 내용 병합 후 덮어쓰기
```

`fileSystem` MCP 서버는 `backend/` 디렉터리를 루트로 노출하므로 상대 경로 `./agent_work_dirs/...` 가 그대로 동작합니다.
