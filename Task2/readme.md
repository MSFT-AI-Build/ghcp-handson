# Task 2: 가위, 바위, 보 게임 만들기 (Copilot Chat)

## Use case: 
- GitHub Copilot Chat기능을 활용하여 가위, 바위, 보 게임을 만들고, 이미지를 추가적인 게임 로직을 추가하는 실습을 통해 Copilot의 활용도를 높입니다.

## 목표:
- Python으로 가위, 바위, 보 게임을 만듭니다.
- 게임을 실행하고 게임 결과를 출력합니다.
- 기본적인 가위, 바위, 보 게임 외에, Lizard, Spock 등의 확장판 게임을 추가합니다.
- Copilot Chat의 `Vision` 기능을 활용하여, 그림파일을 붙여넣기 하고, 이를 기반으로 코드를 제안받아 봅니다.
- Copilot Chat의 `Review` 기능을 활용하여, 코드에 대한 리뷰를 받아 봅니다.
- `Review`에 Custom instruction을 제공하여, 원하는 형태로 리뷰를 받아 봅니다.

## Step 1: 가위, 바위, 보 게임 만들기
### Copilot Chat 시작하기
- Copilot Chat을 이용하여, 가위, 바위, 보 게임을 만들 수 있는 코드를 요청합니다.<br>
사용자가 가위,바위,보 중 하나를 선택하고, 컴퓨터와 대결하는 로직으로 구성합니다.<br>
- 먼저 "가위바위보.py" 새파일을 만듭니다.<br>
<img width="269" height="253" alt="image" src="https://github.com/user-attachments/assets/9252f597-1df4-4449-ac6c-19fc0ca0c958" /><br>

- **Copilot Chat**을 실행합니다. <br>
우측 상단의 대화아이콘을 클릭하면, 대화형 Chat 창이 열립니다.<br>
<img width="907" height="263" alt="image" src="https://github.com/user-attachments/assets/9b2f1c9d-1f5c-49b0-a5a2-a38d1b77ec3f" /><br>
- 이미 채팅창이 띄워진 경우라면, 새로운 채팅으로 시작합니다.<br>
<img width="409" height="80" alt="image" src="https://github.com/user-attachments/assets/c5b02776-e038-4da3-a1cf-9c7c46985952" /><br>
- 참조하는 파일 코드가 이미 있다면, X로 제외를 시킵니다.<br>
그리고 Chat 모드는 **Ask**로 변경해줍니다. (Agent 모드는 Task3에서 실습합니다)<br>
<img width="431" height="133" alt="image" src="https://github.com/user-attachments/assets/5c41d1f4-d710-41e4-889d-b43431ac5f7e" /><br>

### 게임 코드 생성 및 적용
- 채팅 창에 아래의 문구를 입력합니다.<br>
`가위,바위, 보 게임을 만든다. 사용자가 가위,바위,보 중 하나를 선택하고, 컴퓨터는 무작위로 선택한다.
사용자의 선택과 컴퓨터의 선택을 비교하여 승패를 결정한다. 사용자가 이기면 "You Win!", 컴퓨터가 이기면 "You lose", 비기면 "Its a tie!"를 출력한다. 사용자가 "exit"를 입력하면 게임을 종료한다.`<br>
<img width="650" height="657" alt="image" src="https://github.com/user-attachments/assets/7bb0e676-2759-44f3-aa06-a89c49254deb" /> <br>
- 생성한 코드를 반영합니다.(Apply in Editor) <br>
<img width="431" height="328" alt="image" src="https://github.com/user-attachments/assets/8715d1bc-0d19-40f0-b76e-e4f9c77b7ee9" /><br>
어느 파일에 반영할지를 물어보고, 조금전 생성한 가위바위보.py로 선택해줍니다.<br>
<img width="322" height="68" alt="image" src="https://github.com/user-attachments/assets/c5886dbe-f05d-4a41-b6d7-a4da7c4961cd" /><br>
변경된 내용을 채크(V)를 선택하여 적용합니다.<br>
<img width="320" height="293" alt="image" src="https://github.com/user-attachments/assets/72d78709-3c9f-44f7-9ec7-1f38fce150e1" /><br>

- 파이썬 코드를 실행하고, 게임 결과를 출력 받아 봅니다.<br>
<img width="286" height="187" alt="image" src="https://github.com/user-attachments/assets/b0af0d64-8548-45a6-86b2-59e785e7708d" /><br>
<img width="817" height="218" alt="image" src="https://github.com/user-attachments/assets/52fde1c8-e681-43ed-8cd6-58e000cc5bef" /><br>

### Inline Chat 기능 사용
- Copilot Chat과 동일한 기능을 코드상에서 direct로 띄워보는 **Inline Chat** 기능을 사용해봅니다.<br>
가위바위보.py 코드에서 일부 영역을 선택하고(While True)  `Ctrl + I` 버튼을 눌러봅니다.<br>
Inline 챗 창이 열리면 지시를 입력할 수 있으며 `for 문으로 바꿔줘` 라고 입력해봅니다.<br>
<img width="416" height="82" alt="image" src="https://github.com/user-attachments/assets/99423282-08be-43ee-9a1d-c24b3c9bc413" /><br>
제안된 코드를 Accept 합니다<br>
<img width="434" height="113" alt="image" src="https://github.com/user-attachments/assets/4e3ca940-a10c-42d4-8961-547c55329fab" /><br>

- Copilot Chat과 마찬가지로, Chat에서 제안받을 LLM 모델을 선택할수 있습니다.<br>
<img width="150" height="295" alt="image" src="https://github.com/user-attachments/assets/aea9c471-5b29-4789-922a-12310f1f9702" /><br>




## Step 2 : Lizard, Spock 추가하기
### Vision 기능으로 이미지 기반 코드 생성
- 만들어진 게임에 추가로 Lizard, Spock의 로직을 Copilot을 활용하여 추가합니다.<br>
   <img width="400" alt="image" src="https://github.com/user-attachments/assets/f48ab55c-8f55-4fda-b075-37a5c0cb21d9" /> <br>

- Copilot Chat에 위 그림파일을 복사하여 Copilot Chat에 붙여넣기 합니다.<br>
    <img width="400" alt="image" src="https://github.com/user-attachments/assets/309c92b7-4c0c-4e80-8baa-6483923a3d08" /><br>
    <img width="400" src="https://github.com/user-attachments/assets/2958ec6e-3c20-425f-b21d-f9b6cd82cf4b" /><br>

- Copilot Chat에 붙여넣기 한 그림파일 'Pasted Image'가 있음을 확인합니다.<br>
    <img width="198" height="99" alt="image" src="https://github.com/user-attachments/assets/a0638f2d-15cd-42d9-8b8d-292185e34d9d" /><br>

- Copilot Chat에 `그림파일데로 Lizard, Spock을 추가해 주세요` 라고 요청합니다.<br>
    <img width="192" height="47" alt="image" src="https://github.com/user-attachments/assets/fdfdc381-370c-4b36-b541-c78c1f3e9778" /><br>

- Copilot Chat에서 제안된 코드를 확인합니다.<br>
    <img width="475" height="715" alt="image" src="https://github.com/user-attachments/assets/c8a3b9b5-1fde-49d7-887f-b705f57822d6" /><br>

- Copilot Chat에서 `Apply to file` 버튼을 클릭하여, 제안된 코드를 적용합니다.<br>
    <img width="147" height="43" alt="image" src="https://github.com/user-attachments/assets/38480cdf-bdc6-4a3d-9f61-f1763a0a0675" /> <br>

- (선택 사항) 코드를 간단하게 줄여 달라 요청해봅니다.<br>
<img width="470" height="235" alt="image" src="https://github.com/user-attachments/assets/4b792eef-e61e-4cab-acd3-58f8a5d9e148" /> <br>
    <img width="436" height="218" alt="image" src="https://github.com/user-attachments/assets/c0135804-8c10-4c4c-b7c3-b1f3ccb00fcb" /> <br>

- Copilot Chat에서 질의했던 히스토리를 살펴볼수 있습니다.<br>
<img width="102" height="36" alt="image" src="https://github.com/user-attachments/assets/85e616af-f1ae-4340-9614-3753432d803a" /><br>


## Step 3: Code Review 사용해 보기
- 작성한 코드에 대한 리뷰 기능을 사용해 봅니다.<br>
특정 영역을 선택한후, 마우스 오른 버튼을 클릭하여 `Generate Code` >  `Review` 를 선택합니다.<br>
<img width="552" height="753" alt="image" src="https://github.com/user-attachments/assets/36228fca-a108-4496-b5f6-079a7d879e5f" /><br>
- 제안된 코드를 적용해봅니다. <br>
<img width="539" height="380" alt="image" src="https://github.com/user-attachments/assets/d22dafac-da1c-4f9d-bf8b-8d2cad280fe9" /><br><br>

### Custom Instruction 설정
- 코딩 규칙을 사용자의 기준으로 Review 할수 있습니다. (가령, 개발팀별 코딩 가이드 라인)<br> 
Copilot에서는 **Custom Instruction** 기능을 통해 사용자의 규칙을 추가할수 있습니다.<br>
- Ctrl + Shift + P를 눌러서 명령 팔레트를 엽니다.<br>
- `Workspace settings(JSON)`을 선택합니다.<br>
.vscode 에 저장되는 settings.json 파일을 통해 사용자 규칙을 추가할수 있습니다.<br>
<img width="445" height="127" alt="image" src="https://github.com/user-attachments/assets/f1a94015-eb25-4995-969f-4a4dc6c02280" /> <br>

- 설정 JSON 파일을 열고, 'github.copilot.chat.codeGeneration.instructions' 을 설정을 추가합니다.<br>
<img width="363" height="87" alt="image" src="https://github.com/user-attachments/assets/3af6ea94-7a6f-4141-96ad-5bb6af790837" /><br>
- 전체 내용을 아래로 복붙하여 수정합니다.<br>
<img width="502" height="165" alt="image" src="https://github.com/user-attachments/assets/8f7b453f-91fd-4ef7-b840-51408484fb24" /><br>
`{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "text": "함수의 이름은 '_'로 시작하고, 변수 네이밍 규칙과 동일하게 작성합니다. 클래스와 생성자의 이름은 파스칼케이스(PascalCase)를 사용합니다. 들여쓰기는 스페이스 2개로 한다."
    }
  ]
}`<br>
- 코드 라인을 예쁘게 정렬해봅니다. `Shift + Alt + F`<br>
<img width="501" height="160" alt="image" src="https://github.com/user-attachments/assets/5779b033-65e9-438d-8659-3e8425b6d5aa" /><br>

- 다시 한번 `Code Review` 기능을 사용하여, 코드에 대한 리뷰를 받아 봅니다.<br>
   <img width="495" height="418" alt="image" src="https://github.com/user-attachments/assets/969bfe07-71c9-4263-aeaf-4cfb09c31445" /> <br>

## 지식 확인:
- 코드 완성 기능과, Copilot Chat 기능의 차이점
- Vision 기능으로 가능한 다른 활용법
- Copilot Chat의 `Code Review` 기능과 custom instruction을 활용하여, 원하는 형태로 리뷰를 받아 보는 방법
