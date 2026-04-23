# Task 3: 나만의 음성비서 앱만들기 (AI 및 LLM활용)
- 간단한 채팅 앱을 로컬에서 생성하고 기동해봅니다.
- 채팅앱에 생성형 LLM을 통해 답변을 받도록 기능을 추가합니다.
- 음성 인식 기능과 음성 출력 기능을 추가합니다.

> **⚠️ 중요사항**  
> 코드 생성 방식은 개인마다 다르며 아래 예시와 다를 수 있습니다.  
> 당황하지 않고 Copilot Chat과 여러 차례 대화하며 질문/답변/수정해 가면서 Copilot 사용에 익숙해지는 것을 목표로 진행해주세요!

## 1단계: 간단한 웹앱 생성
### 1-1. Copilot Chat 시작하기
- VS Code 우측의 Copilot Chat을 엽니다. <br>
- 이전 질문했던 내용 참조하지 않고 새로운 채팅으로 시작합니다.(New Session) <br>
<img width="1151" height="645" alt="image-3" src="https://github.com/user-attachments/assets/dc768b6e-9698-40fb-a70c-9c8cbffe89cc" />
<br>

### 1-2. 웹앱 코드 생성
- Agent 모드로 진행합니다<br>
<img width="1150" height="645" alt="image-2" src="https://github.com/user-attachments/assets/391d5c77-6a36-4561-ac48-bf5c6dbf367b" />

- 간단한 파이썬 웹앱 코드를 생성해달라고 Copilot Chat에 입력합니다.
  
`
파이썬 코드로, 웹화면을 띄워주는 코드를 새로 만들어주고, 상단에는 사용자 Input을 받고 아래는 send 버튼을 만들어줘
`
<br>

### 1-3. 프로젝트 워크스페이스 생성
- 가이드 해주는대로 지시를 따릅니다. <br>
(파일 및 디렉토리를 필요에 따라 생성하게 되며, 사용자는 허용할지 (Allow)를 선택하고, 생성된 파일을 유지할지 여부를 클릭해서 결정합니다.<br>
<img width="225" height="647" alt="image-4" src="https://github.com/user-attachments/assets/5447ef8e-b756-4e04-a777-97603191b086" />
<br>

### 1-4. 앱 실행 및 문제 해결
-  app.py가 생성된 것을 확인하고, 실제 App을 지시에 따라 실행해봅니다.<br>
<img width="1151" height="647" alt="image-5" src="https://github.com/user-attachments/assets/72fa44c1-221b-45b6-a77a-594d934538a0" />
<br>
- 실행하면, 웹 브라우저를 오픈하게 됩니다. <br>
<img width="895" height="615" alt="image-6" src="https://github.com/user-attachments/assets/06a40d1b-c688-4239-a339-a252faa45bc0" />
<br>
<img width="651" height="486" alt="image-7" src="https://github.com/user-attachments/assets/6c207c1f-fc55-4774-a4b9-43f2ba0dcd71" />
<br>
- 웹앱이 잘 기동한것을 확인했습니다.

- *** 진행과정중 에러발생시 *** Copilot Chat에 질문하면서 문제를 해결해봅니다. <br>
에러 이미지를 캡쳐하여 Chat에 붙여넣어도 됩니다<br>

## 2단계: LLM (ChatGPT) 연동하기
### 2-1. LLM 기능 추가 요청
- Copilot Chat에 추가 보완하고자 하는 내용을 추가합니다. <br>
`사용자로부터 받은 Input 값을 Azure openAI의 gpt4.1 로 보내고 , 나온 결과를 화면 상단에 출력해주도록 코드를 추가하고 싶어. 코드는 최소한만 수정하고 간단하게 알려줘. API키와 URL은 env.example 파일을 참고해줘`<br>
- 변경 업데이트 된 내용 확인후 허용하고, 실행 방법을 확인해봅니다. <br>
- 실행도 Chat에 지시할수 있습니다. (예 .env 파일을 생성해달라고 지시)<br>
<img width="353" height="624" alt="image-8" src="https://github.com/user-attachments/assets/fc901985-7ebc-486b-b1b8-c85484faf015" />

<br>
> 참고) 아래 코드 가이드 순서는 개인마다 다를수 있으며, LLM에서 사용되는 gpt등 주요 API 키는 `Task3/env.example` 를 사용하시면 됩니다<br>

### 2-2. 코드 적용 및 테스트
- 이제 app.py 로 파이선을 실행합니다. <br>
<img width="896" height="321" alt="image-10" src="https://github.com/user-attachments/assets/3073d70e-3ef2-46f0-8a1a-50ce491b5f53" />
<br>
- gpt를 통한 웹 채팅 서비스가 기동됩니다. <br>
<img width="494" height="285" alt="image-11" src="https://github.com/user-attachments/assets/6ba8a575-9c4e-42bb-9275-6e9d85f6e3f5" />
 <br>

## 3단계 : AI 음성 인식 서비스 추가
### 3-1. 음성 인식 기능 요청
- Copilot Chat에 음성인식 기능을 추가해 달라고 요청합니다.<br>
`자 이제, App에 음성인식 기능을 붙이려고해. 기존 코드에 변경을 최소화하고, 최대한 간단하게 코드 수정할 부분을 위주로 알려줘.
먼저, 사용자 Input Text 우측에 마이크 버튼을 추가해주고, 누르면 사용자의 음성을 Input으로 받고, Azure의 Speech to Text API를 사용해서 인식된 Text 결과는 Input 창에 적어준다. 관련된 API정보는 env.example파일을 참고해`<br>
<img width="345" height="588" alt="image-12" src="https://github.com/user-attachments/assets/fcfec816-3f05-4cee-8c2f-41704e89e597" />
<br>
- 정상적으로 수정됐다면 웹화면에서 마이크 버튼 누른후 음성 인식이 정상적으로 됐다면 성공입니다. <br>
<img width="522" height="358" alt="image-13" src="https://github.com/user-attachments/assets/082ceb20-1aa6-44ae-92f7-e93ade6c487d" />
<br>


### 3-3. 음성 출력 기능 추가
- 이제 Text 결과도 음성으로 함께 출력하는 기능을 붙여봅니다.<br>
Copilot Chat에 다음과 같이 요청해봅니다.<br>
`자 이제, 출력된 Text를 Speech로 목소리로도 출력하는 것을 추가해줘. 음성 출력에 사용되는 API도 env.example 파일을 참고하면 돼`<br>
<img width="486" height="338" alt="image-14" src="https://github.com/user-attachments/assets/b6a03847-e7aa-491d-af25-a15b8f58842e" />
<br>
- 질문의 답변이 텍스트 + 음성으로 함께 나온다면 성공적으로 완료 되었습니다 .<br>

### 3-4. 음성 커스터마이징 (추가 미션)
- (참고) Azure에서는 다양한 한국어 음성을 지원하고 있고, 다양한 언어를 읽을수 있습니다. 추가 미션으로 목소리를 다르게 바꿔달라고 요청해봅니다.<br>
`음성을 좀 더 고급 음성모델로 바꿔줘. 한국어 위주이지만 멀티음성 지원되는 걸로 추가해주고, 음성은 사용자가 선택할수 있도록 해줘`

<img width="346" height="593" alt="image-15" src="https://github.com/user-attachments/assets/f8df4d06-2a1d-4b3e-bbd9-77abc8ad6244" />
<br>
<img width="480" height="402" alt="image-16" src="https://github.com/user-attachments/assets/2014dd5e-d663-42b5-beee-4957aa7b6654" />
<br>



> **💡 참고사항 (Agent 모드와 Ask 모드 차이)**
> - **Ask 모드**: 챗에 단계별 질문과 답변을 통해 사용자가 직접 코드를 수정하고 적용해야함. 채팅 모드
> - **Agent 모드**: AI가 단계별 필요한 파일을 생성하고 코드를 수정하고 실행까지 할수 있는 모드
> 
> 복잡한 프로젝트 시작 시에는 Agent 모드가, 기존 코드 수정이나 세부 조정에는 Ask 모드가 더 적합합니다.
<br>

Task3을 모두 완료 하였습니다.<br><br>





















  
