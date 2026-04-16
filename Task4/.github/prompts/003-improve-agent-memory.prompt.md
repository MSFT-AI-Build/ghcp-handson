# 목표
에이전트마다 work directory 를 만들어서, 그 안에 에이전트 spec 이나 memory 를 저장하는 구조로 개선해봅시다. AGENT.md / MEMORY.md 의 읽기·쓰기는 별도 Native Tool 을 만들지 않고 **File System MCP 서버**를 통해 처리한다.

# 아키텍처
```
User ──► Chat UI ──► REST API Server
                           │
                  Supervisor Agent (agent:main)
                  ┌────────┴────────┐
                  │                 │
           Native Tools        MCP Bridge Tools
           (직접 tool calling)  (mcp_list_tools, mcp_call_tool)
                                    │
                         ┌──────────┼──────────┐
                         ▼          ▼          ▼
                    File System  Google Search  Notion
                    MCP Server   MCP Server    MCP Server
                         │
                         ▼
               ./agent_work_dirs/
               ├── supervisor/
               │   ├── AGENT.md        ← role, description, capabilities
               │   └── MEMORY.md       ← 대화 기억, 중요 정보
               └── mcp_config.json     ← MCP 서버 연결 정보
```

## Memory 읽기·쓰기 흐름 (File System MCP 활용)
```
1) 대화 시작 — memory 로드
   Agent ──tool_call──► mcp_list_tools(server="filesystem")
                         └─► tool 목록 반환 (read_file, write_file, ...)

   Agent ──tool_call──► mcp_call_tool(
                           server="filesystem",
                           tool="read_file",
                           arguments={"path": "./agent_work_dirs/supervisor/MEMORY.md"}
                         )
                         └─► MEMORY.md 내용 반환 → context 로 활용

2) 대화 중 — 중요 정보 발생 시 즉시 memory 저장
   Agent ──tool_call──► mcp_call_tool(
                           server="filesystem",
                           tool="read_file",
                           arguments={"path": "./agent_work_dirs/supervisor/MEMORY.md"}
                         )
                         └─► 기존 MEMORY.md 내용 읽기

   Agent ──tool_call──► mcp_call_tool(
                           server="filesystem",
                           tool="write_file",
                           arguments={
                             "path": "./agent_work_dirs/supervisor/MEMORY.md",
                             "content": "<기존 내용 + 새로운 기억 병합>"
                           }
                         )
                         └─► MEMORY.md 에 기록
```

# 개선 방향

## Work Directory 생성
- 에이전트가 생성될 때 고유한 work directory (예: `./agent_work_dirs/{agent_id}/`) 가 자동으로 생성되고, 해당 디렉토리 경로가 에이전트 인스턴스에 저장
- 에이전트의 work directory 안에는 AGENT.md, MEMORY.md 파일이 존재

## 파일 역할
- **AGENT.md**: 에이전트의 description, role, capabilities 등을 마크다운 형식으로 저장
- **MEMORY.md**: 에이전트가 대화 중에 기억해야 할 중요한 정보나 과거 대화 내용 등을 저장

## Memory 활용 흐름
- 별도의 `load_memory` / `save_memory` Native Tool 을 만들지 않는다.
- 대신, 002 에서 구성한 **File System MCP 서버**의 `read_file` / `write_file` tool 을 MCP Bridge Tool (`mcp_call_tool`) 을 통해 호출하여 MEMORY.md 를 읽고 쓴다.
- 에이전트는 **대화 종료 시**가 아니라, **대화 중 중요한 정보가 나올 때마다 즉시** MEMORY.md 에 저장한다.
- 저장 시점의 예:
  - 사용자가 선호도, 설정, 요구사항 등을 언급했을 때
  - 중요한 결정이나 합의가 이루어졌을 때
  - 작업 결과나 핵심 발견 사항이 나왔을 때
  - 다음 대화에서 참고해야 할 맥락이 생겼을 때
- 저장할 때는 기존 MEMORY.md 를 먼저 읽은 뒤, 새로운 내용을 병합하여 덮어쓴다.

## System Prompt 에 포함할 Memory 지침 예시
```
## Memory
당신의 work directory 는 ./agent_work_dirs/supervisor/ 입니다.
- 대화를 시작할 때 mcp_call_tool 을 사용하여 MEMORY.md 파일을 읽고, 이전 기억을 참고하세요.
- 대화 중 중요한 정보(사용자 선호, 결정 사항, 핵심 결과 등)가 나오면 즉시 MEMORY.md 에 저장하세요.
  - 저장 전에 기존 MEMORY.md 를 읽어서 내용을 병합한 뒤 write_file 로 저장합니다.
  - 대화 종료까지 기다리지 말고, 중요한 정보가 나오는 시점에 바로 기록하세요.
- AGENT.md 파일에는 당신의 역할과 능력이 정의되어 있습니다. 필요 시 참고하세요.
```
