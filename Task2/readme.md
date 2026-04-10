# Task 2: 간단한 웹 게임 만들기 (Copilot Chat)

## Use case:
- GitHub Copilot Chat 기능을 활용하여 2048 웹 게임을 만들어 봅니다. Copilot Chat의 다양한 기능(Ask, Vision, Code Review)을 실습하며 활용도를 높입니다.

## 목표:
- HTML/CSS/JavaScript로 2048 게임을 만듭니다.
- Copilot Chat을 활용하여 게임 로직과 UI를 단계적으로 구현합니다.
- Copilot Chat의 `Vision` 기능을 활용하여, 디자인 이미지를 기반으로 코드를 제안받아 봅니다.
- Copilot Chat의 `Review` 기능을 활용하여, 코드에 대한 리뷰를 받아 봅니다.
- `Review`에 Custom Instruction을 제공하여, 원하는 형태로 리뷰를 받아 봅니다.

---

## 2048 게임이란?
> 4×4 그리드에서 같은 숫자의 타일을 합쳐 **2048** 타일을 만드는 슬라이딩 퍼즐 게임입니다.
> - 방향키(↑↓←→)로 타일을 이동합니다.
> - 같은 숫자의 타일이 충돌하면 합쳐져 두 배가 됩니다.
> - 더 이상 이동할 수 없으면 게임 오버입니다.

---

## Step 1: 기본 2048 게임 만들기

### Copilot Chat 시작하기
1. `Task2/src/` 폴더 아래에 `index.html` 파일을 새로 생성합니다.
2. **Copilot Chat**을 실행합니다. (우측 상단의 대화 아이콘 클릭)<br>
   - 이미 채팅창이 열려 있다면, 새로운 대화를 시작합니다.
   - Chat 모드는 **Ask**로 설정합니다. (Agent 모드는 Task3에서 실습합니다)

### 게임 코드 생성 및 적용
- 채팅 창에 아래 프롬프트를 입력합니다.

```
2048 게임을 HTML, CSS, JavaScript로 만들어줘.
하나의 index.html 파일에 모든 코드를 포함해줘.
요구사항:
- 4x4 그리드 기반
- 방향키(↑↓←→)로 타일 이동
- 같은 숫자 타일이 충돌하면 합산
- 현재 점수 표시
- 게임 오버 판정 (이동 불가 시)
- New Game 버튼으로 재시작
- 타일 숫자별로 다른 배경색 적용
```

3. Copilot이 생성한 코드를 확인합니다.
4. **Apply in Editor** 버튼을 클릭하여 `index.html`에 코드를 적용합니다.
5. 브라우저에서 `index.html`을 열어 게임이 동작하는지 확인합니다.
   - VS Code에서 파일을 우클릭 > `Open with Live Server` 또는 터미널에서 아래 명령 실행:
   ```bash
   cd Task2/src && python3 -m http.server 8080
   ```
   - 브라우저에서 `http://localhost:8080` 으로 접속합니다.

6. 방향키를 눌러 타일이 이동하고, 같은 숫자가 합쳐지는지 확인합니다.

### Inline Chat으로 코드 수정하기
- `index.html` 코드에서 그리드 렌더링 부분을 선택하고, `Ctrl + I`로 **Inline Chat**을 열어봅니다.
- 예시: `타일이 합쳐질 때 애니메이션 효과를 추가해줘` 라고 입력합니다.
- 제안된 코드를 확인하고 **Accept** 합니다.

---

## Step 2: 게임 기능 확장하기

### Vision 기능으로 디자인 개선
- 2048 게임의 원본 디자인 이미지를 검색하여 캡처하거나, 원하는 UI 디자인 스케치를 준비합니다.
- Copilot Chat에 이미지를 **붙여넣기(Ctrl+V)** 합니다.
- Copilot Chat에 아래와 같이 요청합니다:

```
이 이미지와 동일한 디자인으로 2048 게임의 CSS를 수정해줘.
타일 색상, 폰트, 레이아웃을 이미지와 최대한 맞춰줘.
```

- 제안된 CSS 코드를 **Apply to file**로 적용하고, 브라우저에서 디자인이 변경되었는지 확인합니다.

### 추가 기능 구현
- Copilot Chat에 아래 프롬프트로 추가 기능을 요청합니다:

```
2048 게임에 다음 기능을 추가해줘:
1. 최고 점수(Best Score)를 localStorage에 저장하고 표시
2. 되돌리기(Undo) 기능 (한 수 되돌리기)
3. 모바일 터치 스와이프 지원
```

- 생성된 코드를 적용하고, 각 기능이 정상 동작하는지 확인합니다.

---

## Step 3: Code Review 사용해 보기

### 코드 리뷰 받기
- 작성한 코드의 JavaScript 영역을 선택한 후, 마우스 오른쪽 버튼을 클릭하여 `Copilot` > `Review and Comment`를 선택합니다.
- Copilot이 제안하는 개선 사항을 확인하고 적용해봅니다.

### Custom Instruction 설정
- 코딩 규칙에 맞는 리뷰를 받기 위해 **Custom Instruction**을 설정합니다.
- `Ctrl + Shift + P` > `Workspace Settings (JSON)` 을 선택합니다.
- 아래 설정을 추가합니다:

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "text": "변수와 함수 이름은 camelCase를 사용합니다. 상수는 UPPER_SNAKE_CASE를 사용합니다. HTML/CSS 클래스는 kebab-case를 사용합니다. 코드에 한글 주석을 포함합니다."
    }
  ]
}
```

- Custom Instruction 적용 후, 다시 한번 **Code Review**를 실행하여 네이밍 규칙 관련 리뷰가 반영되는지 확인합니다.

---

## 지식 확인:
- Copilot Chat의 **Ask 모드**를 활용하여 웹 게임 코드를 생성하는 방법
- **Vision** 기능으로 이미지 기반 디자인 코드를 생성하는 방법
- **Inline Chat**으로 특정 코드 영역을 빠르게 수정하는 방법
- **Code Review** 기능과 **Custom Instruction**을 활용한 코드 품질 관리 방법
