# 🚀 Task 4: MCP
MCP는 LLM 기반 애플리케이션이 외부 서비스나 리소스와 표준화된 방식으로 통신할 수 있도록 하는 프로토콜입니다. 즉, AI 모델이 파일시스템, GitHub, Slack 등 다양한 외부 도구를 안전하고 일관된 인터페이스(JSON-RPC)로 호출할 수 있게 합니다.
![mcp drawio-1](https://github.com/user-attachments/assets/2c31729e-773b-4e76-86cb-fcd316f8bf08)


## ✅ Visual Studio Code 내 MCP 를 이용한 Copilot Agent Mode
MCP(Model Context Protocol) 서버를 VS Code Copilot Agent Mode 와 연계하여 외부 도구(Context)를 활용한 답변 생성 흐름을 실습합니다.

<img width="593" height="400" alt="Screenshot 2025-11-06 at 9 39 41 PM" src="https://github.com/user-attachments/assets/dd9c3d99-fda3-4310-8790-7f616031f0ad" />


### ⚠️ 준비 사항
1. VS Code 최신 버전 & GitHub Copilot 확장 설치
2. 명령 팔레트 열기: macOS `⇧⌘P`, Windows/Linux `Ctrl+Shift+P`
3. `Chat: Open Chat (Agent)` 실행 (Agent 전용 채팅 열기)
4. Copilot Chat 패널 상단 `+` 로 새 Chat 시작

### 🛜 MCP 서버 등록 개요
Copilot Agent Mode 에서는 채팅 입력 시 `#<server-id>` 를 붙여 해당 MCP 서버의 도구/정보를 LLM 컨텍스트로 주입할 수 있습니다. 먼저 필요한 MCP 서버들을 등록합니다.

#### 1) MCP 서버 추가
명령 팔레트 (macOS `⇧⌘P`, Windows/Linux `Ctrl+Shift+P`) 에서 `MCP: Add Server...` 실행 후 아래 항목을 순서대로 등록합니다.

| ID | Description | Type | URL/Name | Properties (환경 변수/자격) |
| --- | --- | --- | --- | --- |
| mcp-microsoft-learn | Microsoft Learn 문서 검색 | HTTP | https://learn.microsoft.com/api/mcp | (필요 없음) |
| mcp-naver-search | Naver 웹/뉴스/블로그 등 검색 | npx | @isnow890/naver-search-mcp | `NAVER_CLIENT_ID=48rMSWKOolV6lIFxl9KA`, `NAVER_CLIENT_SECRET=s2Zopj__5q` |
| mcp-notion | Notion 워크스페이스 페이지/DB 접근 | npx | @notionhq/notion-mcp-server | `NOTION_TOKEN=ntn_l77681213418E7VxzNPzPECYWvbhPxZuDmpiEUiYcSL9Ba` |

#### 2) MCP 서버 상태 확인
명령 팔레트에서 `MCP: List Server` 실행 → 등록된 서버가 `Running` 이면 정상입니다. 만약 `Error` 나 `Stopped` 인 경우:
| 증상 | 원인 후보 | 조치 |
| --- | --- | --- |
| Stopped | 잘못된 명령 / 패키지 설치 실패 | npx 패키지명 재확인, Node 버전 18+ 확인 |
| Error (Auth) | 잘못된 자격 증명 | 환경 변수 값 재입력, 토큰 유효성 확인 |
| Timeouts | 네트워크 차단 | 프록시/방화벽 설정 점검 |

### 💡 `mcp-microsoft-learn` 사용 예시
채팅 입력창에 `#mcp-microsoft-learn` 을 추가하고 아래 질문을 입력해 보세요:
```
Azure Machine Learning 사용 시 Private Network(Managed VNet 또는 사용자 정의 VNet) 구성 절차를 단계별로 정리해줘.
```

### 💡 `mcp-naver-search` 사용 예시
채팅 입력창에 `#mcp-naver-search` 추가 후:
```
오늘 현대자동차 관련 주요 뉴스 헤드라인 5개만 요약해줘. 각 기사별 핵심 키워드도 같이.
```

### 💡 `mcp-notion` 사용 예시
채팅 입력창에 `#mcp-notion` 추가 후 ( `<사용자이름>` 은 본인으로 교체 ):
```
MCP 페이지 하위에 <사용자이름>_PYTHON_CODING_STYLE 페이지를 만들어줘. 페이지 내용은 아래 지침을 반영하고 필요한 추가 항목이 있으면 제안 후 포함해줘.
- 독스트링: Google Style
- 로깅: `logging` 모듈 사용 (print 금지)
- 상대 import 지양 (절대 경로 사용 권장)
```

> 💡 Tip: 한 번에 너무 많은 MCP 서버를 붙이지 말고, 목적별로 필요한 서버만 `#` 로 추가한 뒤 응답 품질과 호출 내역을 점진적으로 관찰하세요.

## ✅ MCP 와 연동하는 AI Agent 만들기
MCP(Model Context Protocol) 서버를 활용하여 Azure OpenAI 모델이 외부 문서/검색/워크스페이스 정보를 도구(Function Calling)로 가져와 풍부한 답변을 생성하는 Python 기반 AI Agent를 만들어 봅니다.

<img width="593" height="400" alt="Screenshot 2025-11-06 at 9 39 44 PM" src="https://github.com/user-attachments/assets/cab68162-5099-4418-85b4-076f6b86697d" />


### ⚠️ 준비 사항
1. VS Code 최신 버전 & GitHub Copilot 확장 설치
2. 명령 팔레트 열기: macOS `⇧⌘P`, Windows/Linux `Ctrl+Shift+P`
3. `Chat: Open Chat (Agent)` 실행 (Agent 전용 채팅 패널)
4. 패널 상단 `+` 로 새 Chat 시작

## ⌨️ AI Agent 제작 프롬프트 템플릿
아래 블록을 Chat 창에 붙여넣고 필요 시 값(엔드포인트/배포명, 토큰 등)을 조정하세요. 이번 실습에서는 3개의 MCP 서버를 모두 활용하는 예시를 포함합니다.
```bash
다음 요구 사항을 만족하는 Python AI Agent 코드를 생성해줘.

[목표]
- 사용자 질문 입력 → Azure OpenAI Chat Completion 호출
- 호출 전 3개 MCP 서버(Microsoft Learn / Naver Search / Notion)의 도구를 조회하여 필요한 컨텍스트(문서, 검색 결과, 페이지 내용)를 수집
- MCP Python SDK 활용: 각 서버 연결 → tool 메타데이터 → OpenAI function schema 변환

[MCP 서버 목록]
1) Microsoft Learn
	- HTTP Endpoint: https://learn.microsoft.com/api/mcp
2) Naver Search
	- 패키지: @isnow890/naver-search-mcp (npx stdio)
	- 필요 환경 변수: NAVER_CLIENT_ID=48rMSWKOolV6lIFxl9KA, NAVER_CLIENT_SECRET=s2Zopj__5q
3) Notion
	- 패키지: @notionhq/notion-mcp-server (npx stdio)
	- 필요 환경 변수: NOTION_TOKEN=ntn_l77681213418E7VxzNPzPECYWvbhPxZuDmpiEUiYcSL9Ba

[MCP Python SDK]
- GitHub: https://github.com/modelcontextprotocol/python-sdk

[Azure OpenAI]
- 필요 환경 변수:
    - AZURE_OPENAI_ENDPOINT="https://yb-kor1.cognitiveservices.azure.com/" 
    - AZURE_OPENAI_API_KEY="<AZURE_OPENAI_API_KEY>"
    - AZURE_OPENAI_DEPLOYMENT="gpt-4.1-mini"
    - AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
- client.chat.completions.create() 사용, tools 인자로 변환된 MCP 함수 목록 전달

[구현 세부]
- MCP tool 호출 payload 에 반드시 "jsonrpc": "2.0" 포함
- HTTP Content-Type: application/json
- 로깅(logging) 사용, print 지양 (구조화된 로그 권장)
- 네트워크/빈 tool 목록/예외 처리 → 재시도(backoff) 또는 경고 출력
- 간단 REPL: 'exit' 입력 시 종료

[출력]
- main.py 예시
- requirements.txt 제안 (openai, mcp, dotenv 등)
- 함수 분리: load_env(), connect_mcp_servers(), build_tools(), chat_loop()
- 3개 서버 각각 tool 변환 적용 예시
```

### 🛠 예시 실행 절차
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 🧪 테스트 질문 예시
1) RBAC:
```
Azure OpenAI 서비스를 사용할 때 필요한 RBAC 역할과 최소 권한 전략을 설명해줘.
```
2) 네트워크 격리:
```
Azure Machine Learning Workspace를 Private Network로 격리할 때 단계별 필수 작업을 정리해줘.
```
