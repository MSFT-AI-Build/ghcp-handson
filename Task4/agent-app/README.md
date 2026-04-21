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
cd backend && pytest -q
cd frontend && npm test -- --run
```

테스트는 LLM(Azure OpenAI) 및 MCP 서버를 모두 **목(mock)** 으로 대체하므로 외부 서비스나 실제 MCP 서버 프로세스 없이 로컬에서 실행 가능합니다.

## Configuration

- `backend/.env` — Azure OpenAI 등 자격 증명 (`.env.example` 참고)
- `backend/mcp_servers/mcp_config.json` — MCP 서버 정의. 기본 항목:
  - `notion` (`@notionhq/notion-mcp-server`, stdio) — `NOTION_TOKEN` 필요
  - `fileSystem` (`@modelcontextprotocol/server-filesystem`, stdio)
  - `braveSearch` (`@brave/brave-search-mcp-server`, http transport) — `BRAVE_API_KEY` 필요

## 도구

- **Native Tool**: `calculate` (안전한 산술 평가)
- **MCP Bridge Tool**: `mcp_list_tools`, `mcp_call_tool` — 위 MCP 서버에 대해 `tools/list`·`tools/call` 중계
