# Task 1: 계산기 함수 완성하기 (Copilot Chat – Agent Mode 사용)

## Use case:
- GitHub Copilot Chat의 **Agent Mode**를 활용하여 미리 준비된 계산기 함수 스켈레톤의 구현을 완성합니다. Agent Mode가 코드를 직접 수정하고, 터미널 명령을 실행하며, 자율적으로 작업을 수행하는 과정을 체험합니다.

## 목표:
- Copilot Chat의 **Agent Mode**를 활성화하고 사용하는 방법을 익힙니다.
- 미완성 스켈레톤 코드(`calculator.py`)에 대해 Agent Mode로 함수 구현을 요청합니다.
- Agent Mode가 코드 수정 → 실행 → 검증까지 자율적으로 수행하는 과정을 관찰합니다.
- 테스트 코드를 Agent Mode에 요청하여 자동 생성합니다.
- VS Code의 Copilot 기본 설정들을 확인합니다.

---

## Step 1: Agent Mode 시작 및 함수 구현

### 1.1 스켈레톤 코드 확인
- `Task1/src/calculator.py` 파일을 엽니다.
- 파일에는 8개의 계산기 함수가 **스켈레톤(함수 시그니처 + docstring만 있고, 본문은 `pass`)** 형태로 준비되어 있습니다.

```python
def add(a: float, b: float) -> float:
    """두 수의 합을 반환합니다."""
    pass

def subtract(a: float, b: float) -> float:
    """두 수의 차를 반환합니다."""
    pass

# ... (multiply, divide, power, modulo, square_root, factorial)
```

- 하단의 `if __name__ == "__main__":` 블록에 간단한 테스트 출력이 포함되어 있으므로, 구현 후 바로 동작 확인이 가능합니다.

### 1.2 Copilot Chat을 Agent Mode로 전환
1. **Copilot Chat**을 실행합니다. (우측 상단의 대화 아이콘 클릭)
2. Chat 창 상단의 모드 선택에서 **Agent**를 선택합니다.
   - Ask 모드: 질문에 대한 답변만 제공
   - Edit 모드: 지정한 파일을 편집
   - **Agent 모드: 코드 수정, 터미널 실행, 파일 생성 등을 자율적으로 수행**

### 1.3 Agent Mode로 함수 구현 요청
- Chat 창에 아래 프롬프트를 입력합니다:

```
calculator.py 파일의 모든 함수 구현을 완성해줘.
각 함수의 docstring에 맞게 구현하고, 에러 처리도 포함해줘.
구현이 끝나면 파일을 실행해서 결과를 확인해줘.
```

- Agent Mode가 자율적으로 수행하는 과정을 관찰합니다:
  1. `calculator.py` 파일을 읽고 분석
  2. 각 함수의 `pass`를 실제 구현 코드로 교체
  3. 터미널에서 `python calculator.py`를 실행하여 결과 확인
  4. 에러가 있으면 자동으로 수정 후 재실행

- Agent Mode가 제안하는 각 단계에서 **Continue** 또는 **Accept**를 눌러 진행합니다.
  > Agent Mode는 파일 수정이나 터미널 실행 전에 사용자 확인을 요청합니다.

### 1.4 실행 결과 확인
- Agent Mode가 실행한 결과가 아래와 유사하게 출력되는지 확인합니다:

```
=== 계산기 테스트 ===
add(2, 3) = 5
subtract(10, 4) = 6
multiply(3, 5) = 15
divide(10, 3) = 3.3333333333333335
power(2, 8) = 256
modulo(10, 3) = 1
square_root(16) = 4.0
factorial(5) = 120
```

---

## Step 2: Agent Mode로 테스트 코드 생성

### 2.1 테스트 코드 요청
- 이어서 Agent Mode Chat에 아래 프롬프트를 입력합니다:

```
calculator.py에 대한 단위 테스트를 pytest로 작성해줘.
정상 케이스와 에러 케이스(0으로 나누기, 음수 제곱근 등)를 모두 포함해줘.
테스트 파일을 생성하고 실행까지 해줘.
```

- Agent Mode가 수행하는 과정을 관찰합니다:
  1. `test_calculator.py` 파일을 자동 생성
  2. 필요하면 `pytest` 패키지를 설치
  3. 테스트를 실행하고 결과를 확인

### 2.2 테스트 결과 확인
- 모든 테스트가 통과하는지 확인합니다.
- 실패하는 테스트가 있다면, Agent Mode에게 수정을 요청합니다:

```
실패한 테스트를 확인하고 수정해줘.
```

---

## Step 3: Agent Mode 활용 심화

### 3.1 기능 추가 요청
- Agent Mode에 추가 기능을 요청하여, 자율적으로 코드를 확장하는 과정을 관찰합니다:

```
calculator.py에 다음 기능을 추가해줘:
1. 평균 계산 함수 (가변 인자)
2. 최대공약수(GCD) 함수
3. 최소공배수(LCM) 함수
추가한 함수에 대한 테스트 코드도 함께 업데이트해줘.
```

### 3.2 문서 생성 요청
- Agent Mode에 문서 생성을 요청합니다:

```
calculator.py의 모든 함수에 대해 사용법을 설명하는 README를 Task1/src/에 만들어줘.
```

---

## Step 4: VS Code의 Copilot 설정 메뉴

### 4.1 언어 설정 변경
- Copilot의 기본 언어를 한국어로 변경합니다.<br>
  `Ctrl + Shift + P` > `Preferences: Open Settings (UI)` 선택 > 검색란에 `copilot locale` 입력 > `ko`로 변경

### 4.2 LLM 모델 변경
- Agent Mode에서 사용하는 LLM 모델을 변경해봅니다.<br>
  Chat 창 상단의 모델 선택 드롭다운에서 다른 모델을 선택할 수 있습니다.
  (사용 가능한 모델은 라이센스 및 시점에 따라 다를 수 있습니다.)

- Reference: [VS Code Copilot settings reference 문서](https://code.visualstudio.com/docs/copilot/copilot-settings)

---

## 참고: Copilot 관련 기술 지원
- [GitHub 도움말: Troubleshoot GitHub Copilot 문서 참조](https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/troubleshoot)
- (기업 관리자) 각종 에러로그, 화면 캡처 등을 첨부하여 GitHub 글로벌 Support에 기술지원 요청/문의할 수 있습니다.
  - [GitHub Support](https://support.github.com)

---

## 지식 확인:
- Copilot Chat의 **Ask / Edit / Agent** 모드 차이점
- Agent Mode가 자율적으로 코드 수정 → 실행 → 검증하는 워크플로우
- Agent Mode를 활용한 테스트 코드 자동 생성
- VS Code의 Copilot 설정 메뉴
