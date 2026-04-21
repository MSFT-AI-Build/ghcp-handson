# 목표
사용자의 다양한 요청을 처리하는 Agent System 을 구성한다. System 은 frontend 와 backend 로 구성된다.


# 아키텍처
```
User ──► Chat UI ──► REST API Server
                           │
                  Supervisor Agent (agent:main)
```

# Overview
- Frontend 와 Backend 는 REST API 로 통신한다.
- SSE/WebSocket은 chat page 에서 streaming 에서만 사용한다.
- 프로젝트 루트: `agent-app/`
  - `backend/` — Python FastAPI 서버
  - `frontend/` — React + TypeScript (Vite) 앱

# Frontend

## 구성
- 최근 UI 트렌드에 맞게 심플하고 직관적인 디자인을 적용한다.
- 위에 page navigation 이 표시되고, 아래에는 page 에 대한 content 를 표시한다.
- 크게 **Chat / Agents / Settings** page 로 구성된다.

## 기술 스택
- React 18 + TypeScript 5 + **Vite** (CRA 대신 사용 — react-scripts 는 TypeScript 5 미지원)
- React Router v6 (BrowserRouter / NavLink)

# Backend

## 기술 스택
- **Python 3.12** + **FastAPI** + **uvicorn** (async ASGI)
- Microsoft Agent Framework: `agent-framework==1.0.1`
- Agent Class: `agent_framework.Agent` 를 사용하고, chat_client 로 `agent_framework.openai.OpenAIChatClient` 를 사용한다. 예제 코드는 https://github.com/microsoft/agent-framework/blob/b89adb280b45a41ab0f0ff28d7947a73d3adbd4c/python/samples/02-agents/providers/azure/openai_client_basic.py#L9 을 참고한다. Client credential 은 API Key 를 사용한다.
- 다른 패키지는 버전을 명시하지 않아도 된다.
- OpenAIChatClient 의 argument 로 api_version 을 전달하지 않아도 된다.
- .env 파일을 사용하여 azure_openai_key, azure_openai_endpoint, azure_openai_deployment 값을 설정할 수 있다. (예: `AZURE_OPENAI_KEY=xxx`)

# 테스트 및 완료 기준 (Agent 연동)

구현과 함께 **자동 테스트**를 추가하고, 로컬/CI에서 **통과**하는 것을 Step 1 완료 조건으로 한다. 외부 LLM 호출은 테스트에서 **목(mock)** 으로 대체한다 (`AGENTS.md`의 “Mock external services in tests” 준수).

## Backend (Python)

- **프레임워크**: `pytest` + `httpx` 의 `AsyncClient` 또는 FastAPI `TestClient` 로 HTTP 레이어 검증.
- **범위**:
  - `GET /health` (또는 동일 목적 엔드포인트): 200 및 응답 본문 스키마.
  - Chat 관련 REST: 요청 본문 검증(400 등), 성공 시 응답 형식(예: `message` / `role` 등 프로젝트에서 정한 필드). **API Key 미제공·무효** 시 기대한 상태 코드(예: 401) 검증.
  - Chat 호출 시 **테스트용 헤더**(가짜 API Key)를 넣어 인증 경로가 타는지 확인한다(실제 Azure 호출은 목).
- **Agent 연동**: `OpenAIChatClient` / `Agent.run` 은 유닛·통합 테스트에서 **목** 처리하여 실제 Azure OpenAI 없이도 통과하도록 한다(고정된 더미 응답 반환).
- **실패 시나리오**: 잘못된 JSON, 필수 필드 누락 등 최소 1건.

## Frontend (TypeScript)

- **프레임워크**: **Vitest** + **Testing Library** (`@testing-library/react`). API는 **MSW(Mock Service Worker)** 로 목 처리하여 Chat 페이지가 **성공/실패 응답**에 맞게 UI를 갱신하는지 검증.
- **범위**:
  - 라우팅: Chat / Agents / Settings 경로 진입 시 기대 레이아웃 또는 제목 표시.
  - Chat: 메시지 전송 시 목 API 호출(메서드·URL·body) 또는 화면에 사용자 메시지·응답 표시. 요청에 **인증 헤더**(API Key)가 포함되는지 검증할 수 있으면 포함한다.
  - Settings: 저장 후 Chat 요청에 동일 credential 이 붙는지(또는 미저장 시 안내·차단) 최소 한 가지 시나리오.

## 통과 조건 (Definition of Done)

- `agent-app/backend`: `pytest` (또는 프로젝트에 명시한 명령) **전부 통과**.
- `agent-app/frontend`: `npm test` 또는 `npm run test` **전부 통과**.
- `README` 또는 `agent-app/README.md`에 아래를 **함께** 적어 재현 가능하게 한다.
  - **실행**: backend 를 띄우는 명령(예: `uvicorn` 모듈 경로·호스트/포트), frontend dev 서버 명령(예: `npm run dev`), 필요 시 사전 단계(가상환경 활성화, `pip install`, `npm install`).
  - **테스트**: 위 `pytest` / `npm test` 명령을 그대로 복사해 실행할 수 있게 한 줄씩.