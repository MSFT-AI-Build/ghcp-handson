# Agent System

**Supervisor + 동적 Worker** 아키텍처의 데모. Supervisor는 사용자 요청을
받아 외부 도구가 필요한 작업을 Worker Agent에게 위임하고, Worker는
Native Tools + MCP Bridge Tools 로 작업을 수행합니다.

## 디렉터리

- `backend/` — FastAPI 앱, 에이전트, Native/MCP Bridge/Delegation Tools, WorkerManager, 테스트
- `frontend/` — React + TS + Vite UI (Chat / Agents / Settings)

## 아키텍처

```
User ──► Chat UI ──► REST API
                       │
              Supervisor Agent (native delegation tools only)
              ├─ delegate_task   ← Worker 동적 생성 + 작업 위임
              ├─ check_workers   ← 상태 조회
              └─ cancel_worker   ← 취소
                       │
                       ▼
              ┌────────────────────────┐
              │  Worker Agent (동적)    │
              │   role/instructions ←  │ Supervisor 가 작업에 맞게 정의
              │  + Native Tools        │
              │  + MCP Bridge Tools    │  (fileSystem / notion / braveSearch 등)
              └────────────────────────┘
```

Supervisor 는 MCP Bridge Tools 를 **직접 가지지 않는다**. 외부 도구가
필요한 작업은 항상 Worker 에게 위임한다.

## 실행

### Backend

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Azure OpenAI 자격 증명 채우기
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
# Backend (Azure OpenAI · MCP 서버 없이 실행 가능)
cd backend && pytest -q

# Frontend
cd frontend && npm test -- --run
```

테스트는 LLM(Azure OpenAI), MCP 서버, Worker LLM 호출을 모두 **목(mock)** 으로
대체하므로 외부 서비스나 실제 MCP 서버 프로세스 없이 로컬에서 실행할 수 있다.

- 파일시스템 의존 테스트는 `pytest` 의 `tmp_path` 픽스처를 사용해 임시
  디렉터리에서 동작하므로 실제 `agent_work_dirs/` 가 비어 있어도 통과한다.
- Worker 실행 테스트는 `WorkerManager(worker_factory=...)` 에 가짜 Worker
  객체(`async run`)를 주입하여 LLM 호출을 우회한다.
- Frontend SSE 테스트는 MSW 로 worker/tool/delta 이벤트 시퀀스를 합성한다.

## Configuration

- `backend/.env` — Azure OpenAI 등 자격 증명 (`.env.example` 참고)
- `backend/mcp_servers/mcp_config.json` — Worker 가 사용하는 MCP 서버 정의:
  - `notion` (`@notionhq/notion-mcp-server`, stdio)
  - `fileSystem` (`@modelcontextprotocol/server-filesystem`, stdio)
  - `braveSearch` (`@brave/brave-search-mcp-server`, stdio)

## Tools

| 영역 | 이름 | 역할 |
| --- | --- | --- |
| Supervisor | `delegate_task` | role/instructions 와 함께 Worker 를 생성하고 작업을 위임 |
| Supervisor | `check_workers` | 활성 Worker 의 ID/상태/결과 조회 |
| Supervisor | `cancel_worker` | 실행 중인 Worker 취소 |
| Worker (Native) | `calculate` | 안전한 산술식 평가 |
| Worker (MCP Bridge) | `mcp_list_tools`, `mcp_call_tool` | MCP 서버 tool 목록/실행 중계 |

## Agent Memory

### Supervisor

- 백엔드가 자동으로 `agent_work_dirs/supervisor/MEMORY.md` 를 읽어 system
  prompt 앞에 주입한다.
- Supervisor 는 답변 안에 다음 마커를 포함하면 된다:

  ```
  [MEMORY_SAVE]
  - 저장할 항목 1
  - 저장할 항목 2
  [/MEMORY_SAVE]
  ```

  백엔드가 이 블록을 추출하여 `MEMORY.md` 에 추가한다 (마커는 사용자에게
  표시되지 않도록 텍스트에서 제거된다).

### Worker

- Worker 는 `mcp_call_tool(server="fileSystem", tool="read_file"/"write_file")`
  를 통해 자신의 `agent_work_dirs/worker-<id>/MEMORY.md` 를 직접 읽고 쓴다.
- Worker 의 `AGENT.md` 에는 Supervisor 가 정의한 role/instructions 가
  기록된다 (작업마다 재작성됨).

### Worker SSE 이벤트

`/api/chat/stream` 은 다음 이벤트를 발행한다:

| event | payload | 설명 |
| --- | --- | --- |
| `delta` | `{text}` | 어시스턴트 텍스트 델타 |
| `tool` | `{name, server?, arguments, result}` | 도구 호출 |
| `worker` | `{id, role, task, status, result?, error?, ...}` | Worker 상태 전이 (`pending`→`running`→`completed`/`failed`/`cancelled`) |
| `done` | `{}` | 종료 |
