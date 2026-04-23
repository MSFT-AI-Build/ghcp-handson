# GitHub Copilot Workshop
안녕하세요. GitHub Copilot Workshop 리포지토리 입니다. 
이 Repository는 여러개의 다른 실습 과제들을 담고 있으며, GitHub Copilot의 기본적인 코드를 제안받는 사용법 부터 추가적인 다른 워크플로우에 이용할 수 있는 방법까지 핸즈온 경험을 기반으로 한 워크샾 내용을 담고 있습니다. 
각 프로젝트는 GitHub Copilot의 서로 다른 사용례를 담고 있으며, 개별적인 실습 과제로서 마무리 됩니다.

## [실습 환경 준비](실습준비.md)

### Codespaces로 시작하기 (권장)
> 가장 빠르게 실습 환경을 구성하는 방법입니다. 별도의 로컬 설치 없이 브라우저에서 바로 시작할 수 있습니다.

1. 아래 버튼을 클릭하여 Codespaces를 생성합니다.

   [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MSFT-AI-Build/ghcp-handson)
2. 창이 뜨면, "Create Codespace" 버튼을 누릅니다<br>
<img width="400" alt="image" src="https://github.com/user-attachments/assets/c0429c81-60aa-4a37-8961-9720e8a9fd3d" />

3. Codespace가 생성되면 VS Code 웹 에디터가 자동으로 열립니다. (처음 활성화시 5분 정도 소요됨)
4. GitHub Copilot, Copilot Chat 확장이 자동 설치되며, **GitHub Copilot CLI**도 기본 설치됩니다.
5. Python, Node.js 등 실습에 필요한 런타임이 모두 포함되어 있어 추가 설치가 필요 없습니다.

### 로컬 환경에서 시작하기
- VS Code를 활용합니다.
  * 다른 IDE도구 (IntelliJ IDEA, Android Studio등)에서, VS Code와 기능적인 차이가 있을 수 있어, 지원되지 않는 실습예가 있을 수 있습니다.
- GitHub Copilot 플러그인을 설치하고, GitHub Copilot Business 라이센스가 있는 계정으로 로그인하여 사용할 수 있는 상태여야 합니다.
- VS Code 및 GitHub Copilot 플러그인은 **최신 버전으로 업데이트 되어 있어야 합니다.**
- 자세한 설치 절차는 [실습준비.md](실습준비.md)를 참고하세요.

  ### 문제 해결
  - Codespaces 환경에서는 GitHub Copilot CLI가 기본으로 설치되어 있습니다.
  - 터미널에서 `copilot` 명령어를 사용하여 GitHub Copilot CLI와 함께 트러블슈팅을 진행할 수 있습니다.
    * 예: `copilot`, `copilot suggest "how to fix permission denied error"`, `copilot explain "git log --oneline"` 등

  ### 언어 및 빌드
  (* 실제 환경까지 모두 셋업이 어려운 경우, 사용법과 코드를 제안받는 것에 목적을 두고 실습)
  - Python: 3.x, VS Code의 Python language pack


## [Task 1](/Task1/readme.md): Task 1: 계산기 함수 완성하기 (Copilot Chat – Ask Mode 사용)
 - GitHub Copilot Chat의 Ask Mode를 활용하여 미리 준비된 계산기 함수 스켈레톤의 구현을 완성합니다.
 - Ask Mode에 질문하고, 제안받은 코드를 직접 에디터에 적용하며 코드를 완성하는 과정을 체험합니다.
 - Copilot Chat의 Ask Mode를 사용하여 코드 구현에 대한 가이드를 받는 방법을 익힙니다.
 - 미완성 스켈레톤 코드(calculator.py)에 대해 Ask Mode로 함수 구현 방법을 질문합니다.

## [Task 2](/Task2/readme.md): 간단한 웹 게임 만들기 (Copilot Chat – Agent Mode 사용)
 - GitHub Copilot Chat의 Agent Mode를 활용하여 2048 웹 게임을 만들어 봅니다.
 - Step by step 프롬프팅만으로 Agent가 코드 생성, 파일 생성, 실행까지 자율적으로 수행하는 과정을 체험합니다.
 - Copilot Chat의 **Agent Mode**를 활성화하고 사용하는 방법을 익힙니다.
 - Agent Mode에 단계적으로 프롬프트를 입력하여 2048 게임을 처음부터 완성합니다.


## [Task 3](/Task3/readme.md): 나만의 음성비서 앱만들기 (AI 및 LLM활용)
- 간단한 채팅 앱을 로컬에서 생성하고 기동해봅니다.
- 채팅앱에 생성형 LLM을 통해 답변을 받도록 기능을 추가합니다.
- 음성 인식 기능과 음성 출력 기능을 추가합니다.

## [Task 4](/Task4/readme.md) : Multi-Agent Playground — 협업하는 AI 만들기
- Github Copilot 를 활용하여 Agent 의 기본 기능을 구축하고 협업 가능한 Agent 를 만들어 갑니다.
- 각 단계는 이전 단계의 기능을 확장하며, 최종적으로 Supervisor Agent가 전문 Worker Agent를 동적으로 생성하여 작업을 위임하는 Multi-Agent 시스템을 구현합니다.
- Github Copilot 이 실수할 때마다, 그 실수를 다시 못하게 AGENTS.md 도 수정해 나가 보세요.
- 미리 작성된 Instruction Prompt 를 Github Copilot Chat(Agent Mode)에 전달하여 각 Step 별로 코드를 생성하고 실행합니다.
