# 목표
Supervisor Agent가 사용자 요청을 받아 **tool calling**으로 Worker Agent에게 작업을 위임하고, Worker의 진행 상태와 결과를 Chat UI에 실시간으로 표시하는 구조로 개선한다. 단, 이전에 있었던 기능(Native Tools, MCP Bridge Tools, File System MCP 기반 memory)은 그대로 유지하면서 agent 구조를 확장한다.

# 아키텍처
```
User ──► Chat UI ──► REST API Server
                           │
                  Supervisor Agent (agent:main)
                  Native Tools ONLY
                  ┌─────────┼─────────┐
            delegate_task  check_    cancel_
                           workers   worker
                  │
                  ▼ (작업에 맞는 Worker 를 동적으로 생성)
            ┌─────────────────────────┐
            │   Worker Agent (동적)    │
            │   - role: Supervisor 가  │
            │     작업에 맞게 정의     │
            │   - MCP Bridge Tools    │
            │   - Native Tools        │
            └────────────┬────────────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         File System  Google Search  Notion
         MCP Server   MCP Server    MCP Server
              │
              ▼
  ./agent_work_dirs/
  ├── supervisor/
  │   ├── AGENT.md
  │   └── MEMORY.md
  ├── worker-{id}/               ← 동적 생성, role 은 그때그때 다름
  │   ├── AGENT.md               ← Supervisor 가 정의한 역할
  │   └── MEMORY.md
  └── mcp_config.json
```

## Tool 배분
```
Supervisor Agent
  └─ Native Tools ONLY
     ├── delegate_task    ← Worker 생성 + 작업 위임
     ├── check_workers    ← Worker 상태 조회
     └── cancel_worker    ← Worker 취소

Worker Agent (동적 생성)
  ├─ Native Tools
  │  └── calculate, ...
  └─ MCP Bridge Tools
     ├── mcp_list_tools   ← MCP 서버의 tool 목록 조회
     └── mcp_call_tool    ← MCP 서버의 tool 호출
         (fileSystem, googleSearch, notion, ...)
```
- Supervisor 는 MCP Bridge Tools 를 **직접 가지지 않는다**. 외부 도구가 필요한 작업은 반드시 Worker 에게 위임한다.
- Worker 만이 MCP Bridge Tools 를 통해 파일 시스템, 검색, Notion 등 외부 도구를 사용할 수 있다.

## Worker 위임 흐름
```
1) Supervisor 가 작업 위임 (Native Tool calling)
   Supervisor ──tool_call──► delegate_task(
                               task="2024년 AI 트렌드를 조사해서 요약해줘",
                               role="AI 기술 리서치 전문가",
                               instructions="최신 AI 논문과 기사를 검색하여 핵심 트렌드를 정리하라."
                             )
                             └─► Worker Agent 동적 생성
                                 - role, instructions 를 Supervisor 가 직접 정의
                                 - work directory 자동 생성
                                 - AGENT.md 에 role/instructions 기록
                             └─► Worker 가 MCP Bridge Tools 로 작업 수행
                             └─► 결과 반환 → Supervisor → User

2) Supervisor 가 Worker 상태 확인
   Supervisor ──tool_call──► check_workers() ──► 활성 Worker 목록 + 상태 반환

3) Supervisor 가 Worker 취소
   Supervisor ──tool_call──► cancel_worker(worker_id="worker-abc123")

4) Worker 의 memory 활용 (MCP Bridge Tool)
   Worker ──tool_call──► mcp_call_tool(
                           server="fileSystem",
                           tool_name="read_file",
                           arguments={"path": "agent_work_dirs/worker-{id}/MEMORY.md"}
                         )
   Worker ──tool_call──► mcp_call_tool(
                           server="fileSystem",
                           tool_name="write_file",
                           arguments={"path": "...", "content": "<기존 + 새 기억 병합>"}
                         )
```

# 개선 방향

## Worker Agent 동적 생성
- Worker 는 미리 정해진 타입(code, research 등)이 **아니다**.
- Supervisor 가 사용자 요청을 분석하고, 해당 작업에 가장 적합한 **role 과 instructions 를 직접 정의**하여 Worker 를 생성한다.
- 예시:
  - "이 코드 리팩토링해줘" → role: "Python 리팩토링 전문가", instructions: "..."
  - "최근 뉴스 정리해줘" → role: "뉴스 리서치 분석가", instructions: "..."
  - "데이터 시각화해줘" → role: "데이터 시각화 엔지니어", instructions: "..."
- 동일한 작업 유형이라도 맥락에 따라 다른 role/instructions 가 부여될 수 있다.

## Worker 생성 시 흐름
1. 고유 ID 부여 (예: `worker-abc123`)
2. work directory 생성 (`./agent_work_dirs/worker-{id}/`)
3. Supervisor 가 정의한 role, instructions 를 AGENT.md 에 기록
4. MEMORY.md 생성 (빈 초기 상태)
5. Worker Agent 인스턴스 생성 (Native Tools + MCP Bridge Tools 등록)
6. 작업 수행 → 결과 반환

## Delegation Native Tools

Supervisor Agent 에만 등록되는 Native Tool 이다.

### `delegate_task(task: str, role: str, instructions: str) -> str`
- 새 Worker Agent 를 동적으로 생성하고 작업을 할당
- `task`: 수행할 작업 내용
- `role`: Worker 의 역할 (Supervisor 가 작업에 맞게 정의)
- `instructions`: Worker 에게 전달할 상세 지시사항 (Supervisor 가 작성)
- Worker 가 작업을 완료하면 결과를 문자열로 반환

### `check_workers() -> str`
- 현재 활성화된 모든 Worker Agent 의 상태를 반환
- 각 Worker 의 ID, role, 현재 상태(running / completed / failed), 작업 설명 포함

### `cancel_worker(worker_id: str) -> str`
- 지정된 Worker Agent 의 작업을 취소

## Supervisor 의 Memory
- Supervisor 도 003 에서 정의한 방식과 동일하게 memory 를 활용하지만, MCP Bridge Tools 가 아닌 **별도 방식**으로 처리한다.
- Supervisor 의 memory 읽기/쓰기는 `delegate_task` 호출 전후에 백엔드가 자동으로 수행한다:
  - 대화 시작 시: 백엔드가 `./agent_work_dirs/supervisor/MEMORY.md` 를 읽어 system prompt 에 주입
  - 대화 중 중요 정보 감지 시: Supervisor 가 응답에 `[MEMORY_SAVE]` 마커와 함께 저장할 내용을 출력하면, 백엔드가 파싱하여 MEMORY.md 에 기록

## Worker 의 Memory
- Worker 는 MCP Bridge Tools 를 가지므로, 003 에서 정의한 방식과 동일하게 File System MCP 서버를 통해 자신의 MEMORY.md 를 읽고 쓴다.
- Worker 의 system prompt 에 자신의 work directory 경로와 memory 지침이 포함된다.
- 작업 수행 중 중요한 정보가 발생하면 즉시 MEMORY.md 에 기록한다.

# Backend

## Supervisor System Prompt
```
## Supervisor Role
당신은 Supervisor Agent입니다. 간단한 요청은 직접 처리할 수 있지만, 복잡하거나 전문적인 작업, 외부 도구(검색, 파일, Notion 등)가 필요한 작업은 반드시 `delegate_task` 를 사용하여 Worker Agent에게 위임해야 합니다.

당신은 MCP 도구를 직접 사용할 수 없습니다. 외부 도구가 필요한 작업은 항상 Worker 에게 위임하세요.

### When to Delegate
- **Delegate** when: 외부 도구(검색, 파일, Notion 등)가 필요할 때, 작업이 집중적인 수행을 요구할 때, 또는 여러 독립적인 작업을 병렬로 실행할 수 있을 때
- **Handle directly** when: 단순한 질문, 인사, 일반 지식으로 답변 가능한 경우

### How to Delegate
1. 사용자의 요청을 분석하여 작업에 가장 적합한 role 과 instructions 를 직접 작성합니다.
2. `delegate_task(task="...", role="...", instructions="...")` 로 Worker 를 생성합니다.
3. 병렬 실행을 위해 여러 작업을 동시에 위임할 수 있습니다.
4. `check_workers` 로 활성 Worker 상태를 모니터링합니다.
5. Worker를 중단해야 할 경우 `cancel_worker` 를 사용합니다.

### Reporting Results
Worker가 작업을 완료하면 결과를 전달받게 됩니다. 해당 결과를 사용자에게 자연스럽게 요약하여 전달하세요.
내부 정보(세션 키, 실행 ID, 토큰 등)는 사용자에게 노출하지 마세요.
```

## Worker 실행 상태 관리
- Worker Agent 실행 상태를 추적하는 WorkerManager 를 구현한다.
- 상태: `pending` → `running` → `completed` / `failed` / `cancelled`
- 상태 변경 시 SSE 를 통해 UI 에 브로드캐스트한다.

# Frontend
- Chat UI 는 Supervisor Agent 와의 상호작용을 통해 사용자에게 작업 진행 상황과 결과를 실시간으로 보여준다.
- Supervisor Agent 가 `delegate_task` 를 호출하면, Worker 의 role 과 작업 내용을 사용자에게 표시한다.
- Worker 의 상태 변경(시작 / 완료 / 실패)을 실시간으로 표시한다.
- 작업이 완료되면 Supervisor 가 요약한 결과를 사용자에게 보여준다.
- Agents 페이지에서 Supervisor 와 활성 Worker 목록, 각각의 role 과 work directory 정보를 조회할 수 있다.

# 테스트 및 완료 기준 (Supervisor · Worker · SSE)

구현과 함께 **자동 테스트**를 추가하고, 로컬/CI에서 **통과**하는 것을 Step 4 완료 조건으로 한다. **Azure OpenAI·실제 MCP 프로세스**는 테스트에서 **목(mock)** 으로 대체한다 (`AGENTS.md`의 “Mock external services in tests” 준수).

## Backend (Python)

- **프레임워크**: `pytest`. HTTP는 Step 1과 동일하게 `httpx` `AsyncClient` 또는 FastAPI `TestClient`로 **기존 API 전체 회귀**를 유지한다.
- **Supervisor 전용 Native Tool** (`delegate_task`, `check_workers`, `cancel_worker`):
  - **WorkerManager** 또는 동등 레이어를 **목 LLM/목 Worker 실행**과 함께 검증: 위임 시 work directory·`AGENT.md` 생성, `check_workers` 반환 스키마, `cancel_worker` 후 상태(`cancelled` 등).
  - Supervisor 가 **MCP Bridge Tool 을 직접 등록하지 않았는지**(아키텍처 제약) 구현 수준이 허용하면 단언한다.
- **Worker Agent**:
  - Worker 실행 경로는 **Agent.run / OpenAIChatClient 를 목**으로 두고, MCP 호출은 Step 2와 같이 MCP Client **목**으로 고정 응답을 반환하게 한다.
- **Supervisor Memory (자동 주입·`[MEMORY_SAVE]`)**:
  - 대화 시작 시 `MEMORY.md` 주입, 응답 내 `[MEMORY_SAVE]` 파싱 후 파일 반영 로직이 있으면 **파일 I/O 또는 목**으로 단위 테스트한다.
- **SSE (Worker 상태 브로드캐스트)**:
  - 상태 전이(`pending` → `running` → `completed` / `failed` / `cancelled`) 시 **이벤트 페이로드**에 worker id·상태가 포함되는지 검증한다. 전체 브라우저 없이 `TestClient` 스트리밍 엔드포인트 또는 브로드캐스트 헬퍼를 직접 호출하는 방식 중 프로젝트에 맞게 선택한다.
- **실패 시나리오** 최소 1건: 예) 존재하지 않는 `worker_id`로 `cancel_worker`, Worker 실패 시 `failed` 처리.

## Frontend (TypeScript)

- **프레임워크**: **Vitest** + **Testing Library**, API는 **MSW**로 목.
- **범위**:
  - Chat: Worker 생성·상태 변경에 따른 UI(역할·작업 요약·진행/완료/실패)가 **목 SSE 이벤트 또는 목 REST**에 맞게 갱신되는지 검증. SSE 전체를 붙잡기 어렵면 **이벤트 핸들러에 가짜 이벤트**를 넣는 단위 테스트로 대체 가능하다.
  - Agents: Supervisor + 활성 Worker 목록, role·work directory 표시가 목 API와 일치하는지 검증.
  - Step 1~3 UI 회귀(라우팅, tool 표시, 기존 Agents/Chat 동작).

## 통과 조건 (Definition of Done)

- `agent-app/backend`: `pytest` **전부 통과**(Step 1~3 테스트 포함 회귀).
- `agent-app/frontend`: `npm test` 또는 `npm run test` **전부 통과**.
- `README` 또는 `agent-app/README.md`에 아래를 **함께** 적어 재현 가능하게 한다.
  - **실행**: backend / frontend 기동 명령, 필요 시 사전 단계(가상환경, `pip install`, `npm install`). Worker·MCP를 로컬에서 실제로 쓸 때는 `mcp_config.json`·`agent_work_dirs/`·MCP 서버 기동을 짧게 적는다.
  - **테스트**: `pytest` / `npm test` 명령을 그대로 복사해 실행할 수 있게 한 줄씩.
  - **테스트 재현**: **LLM·MCP 실프로세스 없이** 테스트만으로 재현하는 방법(예: “테스트는 Supervisor/Worker·MCP 목, 파일은 tmp”)을 한 줄 이상.
