# 목표
Agent 가 호출할 수 있는 tools 을 components 형태로 분리하여 관리한다. Tool 은 **Native Tool**(Python 함수)과 **MCP Tool**(MCP 서버를 통해 제공되는 도구) 두 가지 유형을 지원한다.

# 아키텍처
```
User ──► Chat UI ──► REST API Server
                           │
                  Supervisor Agent (agent:main)
                  ┌────────┴────────┐
                  │                 │
           Native Tools        MCP Bridge Tools
           (직접 tool calling)  (mcp_list_tools, mcp_call_tool)
                  │                 │
                  ▼                 ▼
           Python 함수들        MCP Client
           - calculate()        (stdio/sse)
           - ...                    │
                         ┌──────────┼──────────┐
                         ▼          ▼          ▼
                    Google Search  Notion    File System
                    MCP Server    MCP Server MCP Server

./agent_work_dirs/
├── mcp_config.json               ← MCP 서버 연결 정보
```

## Tool 호출 흐름
```
1) Native Tool 호출 (일반 tool calling)
   Agent ──tool_call──► calculate(expression="1+2") ──► 결과 반환

2) MCP Tool 호출 (2단계)
   Agent ──tool_call──► mcp_list_tools(server="notion")
                         └─► MCP 서버에 tools/list 요청
                         └─► tool 목록 + input schema 반환

   Agent ──tool_call──► mcp_call_tool(server="notion", tool="search", arguments={...})
                         └─► input schema 에 맞춰 arguments 구성
                         └─► MCP 서버에 tools/call 요청
                         └─► 결과 반환
```

# Tool 유형

## 1. Native Tool
- Python 함수로 직접 구현된 도구
- `agent_framework` 의 tool decorator 또는 함수를 사용하여 Agent 의 tools 인자로 직접 등록
- Agent 가 일반적인 tool calling 으로 바로 호출 (별도 라우팅 없음)
- 예: 계산 등

## 2. MCP Tool (Model Context Protocol)
- 외부 MCP 서버가 제공하는 도구를 MCP 클라이언트를 통해 호출
- MCP 서버는 **stdio** 또는 **SSE** 두 가지 transport 방식을 지원
- Agent 는 MCP Tool 을 직접 알지 못하고, **MCP Bridge Tool** (`mcp_list_tools`, `mcp_call_tool`) 을 통해 간접적으로 호출
- MCP 서버는 별도 프로세스로 실행되며, Agent 와는 JSON-RPC 로 통신

## MCP Bridge Tools

Agent 에 등록되는 두 개의 Native Tool 로, MCP 서버와의 통신을 중개한다.

### `mcp_list_tools(server: str) -> list`
- 지정된 MCP 서버에 `tools/list` 요청을 보내 사용 가능한 tool 목록과 각 tool 의 input schema 를 반환
- Agent 는 이 결과를 보고 어떤 MCP tool 을 호출할지, 어떤 arguments 를 넘길지 결정

### `mcp_call_tool(server: str, tool: str, arguments: dict) -> str`
- 지정된 MCP 서버의 특정 tool 을 호출
- `arguments` 는 `mcp_list_tools` 에서 받은 input schema 에 맞춰 Agent 가 구성
- MCP Client 가 `tools/call` 요청을 MCP 서버로 전달하고 결과를 반환

# MCP 서버 설정 (`mcp_servers/mcp_config.json`)

MCP 서버 연결 정보는 하나의 JSON 파일로 관리한다. 각 서버에 대해 transport 방식, 실행 명령어, 환경변수 등을 정의한다.

```json
{
  "mcpServers": {
    "notion": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "OPENAPI_MCP_HEADERS": "{\"Authorization\": \"Bearer ${NOTION_TOKEN}\", \"Notion-Version\": \"2025-09-03\"}"
      }
    },
    "fileSystem": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./"]
    },
    "googleSearch": {
      "command": "noapi-google-search-mcp",
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

# 개선 방향

## Native Tool 등록
- Native Tool 은 Python 함수로 구현하고, Agent 생성 시 `tools` 인자로 직접 전달한다.
- Agent 가 일반적인 tool calling 으로 바로 호출하므로 별도 라우팅 레이어가 불필요하다.

## MCP Bridge Tool 등록
- `mcp_list_tools` 와 `mcp_call_tool` 두 함수를 Native Tool 과 동일하게 Agent 의 `tools` 인자로 등록한다.
- 이 두 함수 내부에서 MCP Client 를 사용하여 MCP 서버와 통신한다.

## MCP Client 구현
- Python MCP SDK (`mcp` 패키지) 를 사용하여 MCP Client 를 구현한다.
- stdio transport: `StdioServerParameters` 로 서버 프로세스를 관리
- SSE transport: `sse_client` 로 HTTP SSE 연결을 관리
- MCP Client 는 서버 lifecycle (초기화 → tool 목록 조회 → tool 호출 → 종료) 을 관리한다.
- MCP 서버가 비정상 종료된 경우 자동 재시작을 시도한다.

## MCP Tool 호출 흐름 (Agent 관점)
1. Agent 가 MCP 도구를 사용하고 싶을 때 먼저 `mcp_list_tools(server="notion")` 을 호출한다.
2. 반환된 tool 목록과 input schema 를 분석하여 적절한 tool 과 arguments 를 결정한다.
3. `mcp_call_tool(server="notion", tool="search", arguments={"query": "..."})` 을 호출하여 실제 작업을 수행한다.
4. 결과를 받아 사용자에게 응답한다.

# Backend

## 기본 MCP 서버
MCP 서버들은 프로세스 initialization 시 `mcp_config.json` 에 정의된 명령어로 실행한다.
기본적으로 아래 MCP 서버들을 지원한다:
- **File System**: https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem
- **NoAPI Google Search MCP**: https://github.com/VincentKaufmann/noapi-google-search-mcp
- **Notion MCP Server**: https://github.com/makenotion/notion-mcp-server

## 필요 패키지
- 이외 MCP 서버별로 필요한 패키지 (예: Notion API 클라이언트, Google Search API 클라이언트 등) 가 있으면 requirements.txt 에 추가한다.
- **NoAPI Google Search MCP** 의 경우 playwright 와 chromium (`playwright install chromium`) 설치가 필요하다.

# Frontend

## Tools 관리 UI
- Agents 페이지 에서 등록된 tool 목록을 조회할 수 있다.
- 각 tool 의 이름, 유형(Native/MCP), 설명, 상태(활성/비활성)를 표시한다.
- MCP 서버의 연결 상태를 표시한다 (connected / disconnected / error).
- Chat 페이지에서는 Agent 가 호출한 tool 과 결과를 대화 흐름에 표시한다. MCP Tool 의 경우 어떤 MCP 서버의 어떤 tool 이 호출되었는지도 함께 표시한다.

# 테스트 및 완료 기준 (Agent · Tool 연동)

구현과 함께 **자동 테스트**를 추가하고, 로컬/CI에서 **통과**하는 것을 Step 2 완료 조건으로 한다. **Azure OpenAI·실제 MCP 서버 프로세스·외부 SaaS API**는 테스트에서 **목(mock)** 또는 **페이크(fake)** 로 대체한다 (`AGENTS.md`의 “Mock external services in tests” 준수).

## Backend (Python)

- **프레임워크**: `pytest`. HTTP는 Step 1과 동일하게 `httpx` `AsyncClient` 또는 FastAPI `TestClient`.
- **Native Tool**:
  - 도구 함수(예: `calculate`)는 **순수 로직** 단위 테스트: 정상 입력·에러 입력(빈 문자열, 나눗셈 0 등) 최소 각 1건.
  - Agent 에 tool 이 등록된 경로는 **LLM/Agent 실행부를 목**으로 두고, tool 호출이 발생하는 시나리오 또는 tool 미사용 시나리오 중 팀이 정한 수준까지 검증.
- **MCP Bridge** (`mcp_list_tools`, `mcp_call_tool`):
  - MCP Client·stdio/SSE·서버 프로세스는 유닛 테스트에서 **목**으로 주입하여 `tools/list`·`tools/call` 결과를 고정 문자열/JSON으로 반환하게 한다.
  - 실패 시나리오 최소 1건: 예) 알 수 없는 `server` 이름, MCP 응답 에러 시 예외 또는 API 에러 매핑.
- **설정**: `mcp_config.json` 로딩·스키마 검증이 있으면, 잘못된 JSON/필수 키 누락에 대한 테스트를 추가한다(선택이 아니라 구현했다면 필수).

## Frontend (TypeScript)

- **프레임워크**: **Vitest** + **Testing Library**. API는 **MSW**로 목.
- **범위**:
  - **Agents** 페이지: tool 목록 API(또는 정적 설정 노출 API) 목 응답에 따라 **이름·유형(Native/MCP)·상태**가 렌더되는지 확인. MCP 연결 상태(`connected` / `disconnected` / `error`) 표시가 있으면 각각 최소 한 번.
  - **Chat**: tool 호출 메타데이터가 포함된 응답(또는 스트림 이벤트)을 목으로 주고, **어떤 tool·(MCP인 경우) server/tool** 이 UI에 드러나는지 확인.

## 통과 조건 (Definition of Done)

- `agent-app/backend`: `pytest` **전부 통과**(Step 1 테스트 포함 회귀).
- `agent-app/frontend`: `npm test` 또는 `npm run test` **전부 통과**.
- `README` 또는 `agent-app/README.md`에 위 명령과, **로컬에서 MCP 실서버 없이** 테스트만으로 재현하는 방법이 한 줄이라도 적혀 있으면 좋다(예: “테스트는 MCP/LLM 목 사용”).
