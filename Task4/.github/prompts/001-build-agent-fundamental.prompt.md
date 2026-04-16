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
- Agent Class: `agent_framework.Agent` 를 사용하고, chat_client 로 `agent_framework.openai.OpenAIChatClient` 를 사용한다. 예제 코드는 https://github.com/microsoft/agent-framework/blob/b89adb280b45a41ab0f0ff28d7947a73d3adbd4c/python/samples/02-agents/providers/azure/openai_client_basic.py#L9 을 참고한다.
- 다른 패키지는 버전을 명시하지 않아도 된다.
- OpenAIChatClient 의 argument 로 api_version 을 전달하지 않아도 된다.