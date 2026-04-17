# Task 1: 계산기 함수 완성하기 (Copilot Chat – Ask Mode 사용)

## Use case:
- GitHub Copilot Chat의 **Ask Mode**를 활용하여 미리 준비된 계산기 함수 스켈레톤의 구현을 완성합니다. Ask Mode에 질문하고, 제안받은 코드를 직접 에디터에 적용하며 코드를 완성하는 과정을 체험합니다.

## 목표:
- Copilot Chat의 **Ask Mode**를 사용하여 코드 구현에 대한 가이드를 받는 방법을 익힙니다.
- 미완성 스켈레톤 코드(`calculator.py`)에 대해 Ask Mode로 함수 구현 방법을 질문합니다.
- Copilot이 제안한 코드를 **직접 에디터에 적용**하고, 터미널에서 실행하여 동작을 확인합니다.
- Inline Chat과 코드 완성(Code Completion) 기능을 함께 활용합니다.
- VS Code의 Copilot 기본 설정들을 확인합니다.

---

## Step 1: Ask Mode로 함수 구현 방법 알아보기

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

### 1.2 Copilot Chat을 Ask Mode로 설정
1. 우측에 열려 있는 **Copilot Chat** 패널을 확인합니다.
2. Chat 창 상단의 모드 선택에서 **Ask**를 선택합니다.
   - **Ask 모드: 질문에 대한 답변과 코드 제안을 제공 (파일을 직접 수정하지 않음)**
   - Plan 모드: 요청을 처리하기 위해 깊게 생각하고 결과를 제공
   - Agent 모드: 코드 수정, 터미널 실행, 파일 생성 등을 자율적으로 수행

### 1.3 Ask Mode로 함수 구현 코드 요청
- Chat 창에 아래 프롬프트를 입력합니다:

```
calculator.py 파일의 모든 함수 구현을 완성하는 코드를 알려줘.
```

- Copilot이 각 함수의 구현 코드를 **제안**합니다. 이 코드를 직접 에디터에 적용해야 합니다.

### 1.4 제안된 코드를 에디터에 적용
- Copilot이 제안한 코드 블록 위에 마우스를 올리면 나타나는 **Apply in Editor** 버튼을 클릭합니다.
  - 적용 대상 파일이 `calculator.py`인지 확인합니다.
- 또는 코드를 복사하여 `calculator.py`에서 각 함수의 `pass`를 직접 교체합니다.
- 변경 사항을 검토한 후 **Accept** 또는 **Ctrl + S**로 저장합니다.

> **Tip**: Ask Mode는 파일을 직접 수정하지 않으므로, 사용자가 코드를 확인한 후 직접 반영하는 과정이 필요합니다. 코드를 이해하고 적용하는 학습 효과가 있습니다.

### 1.5 터미널에서 직접 실행하여 확인
- VS Code 터미널(`Ctrl + ~`)을 열고, 아래 명령어를 실행합니다:

```bash
cd Task1/src && python calculator.py
```

- 실행 결과가 아래와 유사하게 출력되는지 확인합니다:

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

- 에러가 발생하면, 에러 메시지를 Copilot Chat에 붙여넣고 수정 방법을 질문합니다:

```
아래 에러가 발생했어. 어떻게 수정하면 될까?
<에러 메시지 붙여넣기>
```

---

## Step 2: Ask Mode 활용 심화

### 2.1 코드 설명 요청
- `calculator.py`의 전체 코드 또는 특정 함수를 선택한 후, Copilot Chat에 아래와 같이 질문합니다:

```
이 코드를 초보 개발자도 이해할 수 있게 한국어로 설명해줘.
```

### 2.2 기능 추가 방법 질문
- Ask Mode에 추가 기능의 구현 방법을 질문합니다:

```
calculator.py에 다음 기능을 추가하려면 어떻게 하면 될까?
1. 평균 계산 함수 (가변 인자)
2. 최대공약수(GCD) 함수
3. 최소공배수(LCM) 함수
코드를 알려줘.
```

- 제안받은 코드를 **Apply in Editor**로 적용하거나 직접 입력합니다.
- 터미널에서 다시 실행하여 정상 동작을 확인합니다.

---

## Step 3: VS Code의 Copilot 설정 메뉴

### 3.1 LLM 모델 변경
- Chat에서 사용하는 LLM 모델을 변경해봅니다.<br>
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
- Copilot Chat의 **Ask / Plan / Agent** 모드 차이점
- Ask Mode로 코드 제안을 받고, **직접 에디터에 적용**하는 워크플로우
- Ask Mode로 에러 디버깅 및 코드 설명을 요청하는 방법
- VS Code의 Copilot 설정 메뉴
