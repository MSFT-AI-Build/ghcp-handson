# Hands-on Lab 4: Multi-Agent Playground — 협업하는 AI 만들기

> GitHub Copilot의 Prompt Files를 활용하여, AI Agent가 도구를 사용하고 기억하고 협업하는 시스템을 4단계에 걸쳐 점진적으로 구축합니다.

## 사전 준비

- Node.js 18+ / Python 3.12+
- Azure OpenAI 리소스 (Endpoint, API Key, 배포된 모델명)
- GitHub Copilot이 활성화된 IDE (Github Codespace / VS Code 등)

## 진행 방법

1. `.github/prompts/` 폴더에서 해당 Step의 Prompt File을 엽니다.
2. Copilot Chat(Agent Mode)에 Prompt File을 전달합니다.
3. Copilot이 생성한 코드를 확인하고 실행합니다.
4. 예시 질문으로 동작을 검증한 뒤, 다음 Step으로 넘어갑니다.

> 각 Step은 이전 단계를 확장하므로, **반드시 순서대로** 진행합니다.

---

## Steps

### Step 1. Agent 기본 구조 구축

| | |
|---|---|
| **Prompt** | `.github/prompts/001-build-agent-fundamental.prompt.md` |
| **한 줄 설명** | Chat UI + REST API + Supervisor Agent로 기본 대화 시스템 구축 |

```
User ──► Chat UI ──► REST API Server ──► Supervisor Agent
```

**예시 질문**:
- "안녕하세요, 당신은 누구인가요?"
- "TypeScript와 JavaScript의 차이점을 알려줘"
- "오늘 할 일 목록을 만들어줘"

---

### Step 2. Tool Components 추가

| | |
|---|---|
| **Prompt** | `.github/prompts/002-add-tool-components.prompt.md` |
| **한 줄 설명** | Native Tool과 MCP Tool을 추가하여 Agent가 외부 도구를 사용할 수 있도록 확장 |

```
Supervisor Agent
├── Native Tools (calculate, ...)
└── MCP Bridge Tools
    └── Google Search / Notion / File System MCP Servers
```

**예시 질문**:
- "123 * 456 + 789를 계산해줘" (Native Tool)
- "최근 AI 관련 뉴스를 검색해줘" (Google Search MCP)
- "내 Notion 페이지에서 회의록을 찾아줘" (Notion MCP)
- "현재 디렉토리의 파일 목록을 보여줘" (File System MCP)

---

### Step 3. Agent Memory 개선

| | |
|---|---|
| **Prompt** | `.github/prompts/003-improve-agent-memory.prompt.md` |
| **한 줄 설명** | Work Directory에 AGENT.md / MEMORY.md를 두어 Agent가 대화 맥락을 기억하도록 개선 |

```
./agent_work_dirs/supervisor/
├── AGENT.md     ← 역할 · 능력 정의
└── MEMORY.md    ← 대화 기억 · 중요 정보
```

**예시 질문**:
- "내 이름은 XX야. 기억해줘" → (새 대화 시작) → "내 이름이 뭐였지?"
- "나는 Python을 주로 사용해" → (새 대화 시작) → "코드 예제를 보여줘" (Python으로 답변하는지 확인)
- "다음 회의는 금요일 3시로 정했어" → (새 대화 시작) → "회의 일정이 어떻게 됐지?"

---

### Step 4. Worker Agent 구현 (Multi-Agent)

| | |
|---|---|
| **Prompt** | `.github/prompts/004-implement-worker-agents.prompt.md` |
| **한 줄 설명** | Supervisor가 작업을 분석하여 전문 Worker Agent를 동적으로 생성하고 위임하는 Multi-Agent 구조 |

```
Supervisor (delegate_task / check_workers / cancel_worker)
    └──► Worker Agent (동적 생성, 역할 자동 부여)
             └── Native Tools + MCP Bridge Tools
```

**예시 질문**:
- "2024년 AI 트렌드를 조사해서 요약해줘" (리서치 Worker 생성)
- "이 Python 코드를 리팩토링해줘" (코드 전문가 Worker 생성)
- "최근 뉴스를 검색하고, 동시에 Notion에서 관련 메모를 찾아줘" (병렬 Worker 생성)
- "현재 진행 중인 작업이 뭐야?" (check_workers)

---

## 전체 흐름 요약

```
Step 1              Step 2              Step 3              Step 4
기본 대화      ───►  도구 사용      ───►  기억 능력      ───►  협업 체계
                                                             
"대화할 수 있는"    "도구를 쓸 수 있는"  "기억할 수 있는"    "협업할 수 있는"
Agent               Agent               Agent               Agents
```