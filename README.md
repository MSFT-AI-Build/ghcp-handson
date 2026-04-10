# GitHub Copilot Workshop
안녕하세요. GitHub Copilot Workshop 리포지토리 입니다. 
이 Repository는 여러개의 다른 실습 과제들을 담고 있으며, GitHub Copilot의 기본적인 코드를 제안받는 사용법 부터 추가적인 다른 워크플로우에 이용할 수 있는 방법까지 핸즈온 경험을 기반으로 한 워크샾 내용을 담고 있습니다. 
각 프로젝트는 GitHub Copilot의 서로 다른 사용례를 담고 있으며, 개별적인 실습 과제로서 마무리 됩니다.

## [실습 환경 준비](실습준비.md)
- VS Code를 활용합니다.
  * 다른 IDE도구 (IntelliJ IDEA, Android Studio등)에서, VS Code와 기능적인 차이가 있을 수 있어, 지원되지 않는 실습예가 있을 수 있습니다.
- GitHub Copilot 플러그인을 설치하고, GitHub Copilot Business 라이센스가 있는 계정으로 로그인하여 사용할 수 있는 상태여야 합니다.
- VS Code 및 GitHub Copilot 플러그인은 **최신 버전으로 업데이트 되어 있어야 합니다.**

  ### 문제 해결
  - 본 리포지토리를 Codespaces 환경에서 실행하면 GitHub Copilot CLI가 기본으로 설치되어 있습니다.
  - 터미널에서 `copilot` 명령어를 사용하여 GitHub Copilot CLI와 함께 트러블슈팅을 진행할 수 있습니다.
    * 예: `copilot`, `copilot suggest "how to fix permission denied error"`, `copilot explain "git log --oneline"` 등

  ### 언어 및 빌드
  (* 실제 환경까지 모두 셋업이 어려운 경우, 사용법과 코드를 제안받는 것에 목적을 두고 실습)
  - Python: 3.x, VS Code의 Python language pack


## [Task 1](/Task1/readme.md): 간단한 함수 코드 작성하기 (**Code 완성** 기능 사용)
 - GitHub Copilot를 활용한 간단한 함수와 테스트 코드를 제안받는 실습입니다. 이를 통해 기본적인 Copilot의 기능을 활용하는 방법을 익힙니다. 
 - GitHub Copilot Log를 확인하여, 오픈소스와 매치되는 코드인 경우 레퍼런스 정보를 확인합니다. 
 - VS Code의 Copilot 메뉴 기본적인 설정들을 변경해 봅니다. 

## [Task 2](/Task2/readme.md): 가위, 바위, 보 게임 만들기 (**Copilot Chat** 기능 사용)
 - GitHub Copilot과 함께 가위, 바위, 보 게임을 만들어 봅니다.
 - Copilot을 통해 테스트 코드를 작성해 봅니다.
 - Copilot chat의 각종 메뉴들을 사용해 봅니다.
 - Copilot Code Review를 통해, 코드에 대한 리뷰를 받아 봅니다.
 - 이미지를 Copilot Chat에 컨텍스트로 제공하고(Vision기능), 코드를 제안받아 봅니다.

## [Task 3](/Task3/readme.md): 나만의 음성비서 앱만들기 (AI 및 LLM활용)
- 간단한 채팅 앱을 로컬에서 생성하고 기동해봅니다.
- 채팅앱에 생성형 LLM을 통해 답변을 받도록 기능을 추가합니다.
- 음성 인식 기능과 음성 출력 기능을 추가합니다.

## [Task 4](/Task4/readme.md) : MCP 서버 연동하기
- MCP 가 무엇일까요 ?
- Visual Studio Code 내 MCP 와 연동되는 Copilot Agent Mode 을 사용해 봅니다.
- MCP 와 연동하는 AI Agent 를 만들어 봅니다.
