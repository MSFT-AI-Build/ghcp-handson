# Task 3: 나만의 음성비서 앱만들기 (AI 및 LLM활용)
- 간단한 채팅 앱을 로컬에서 생성하고 기동해봅니다.
- 채팅앱에 생성형 LLM을 통해 답변을 받도록 기능을 추가합니다.
- 음성 인식 기능과 음성 출력 기능을 추가합니다.

> **⚠️ 중요사항**  
> 코드 생성 방식은 개인마다 다르며 아래 예시와 다를 수 있습니다.  
> 당황하지 않고 Copilot Chat과 여러 차례 대화하며 질문/답변/수정해 가면서 Copilot 사용에 익숙해지는 것을 목표로 진행해주세요!

## 1단계: 로컬에서 간단한 웹앱 생성
### 1-1. Copilot Chat 시작하기
- VS Code 우측 상단의 Copilot 아이콘을 선택하여, Copilot Chat을 엽니다. <br>
<img width="260" height="130" alt="image" src="https://github.com/user-attachments/assets/a902531e-ca2b-42cd-9d85-13e0cb8e16aa" /><br>
- 이미 채팅창이 띄워진 경우라면, 새로운 채팅으로 시작합니다.<br>
<img width="409" height="80" alt="image" src="https://github.com/user-attachments/assets/c5b02776-e038-4da3-a1cf-9c7c46985952" /><br>
- 참조하는 파일 코드가 이미 있다면, X로 제외를 시킵니다.<br>
그리고 Chat 모드는 **Ask**로 변경해줍니다. (Agent 모드는 Task3 마지막에서 실습합니다)<br>
<img width="431" height="133" alt="image" src="https://github.com/user-attachments/assets/5c41d1f4-d710-41e4-889d-b43431ac5f7e" /><br>

### 1-2. 웹앱 코드 생성
- 간단한 파이썬 웹앱 코드를 생성해달라고 Copilot Chat에 입력합니다. <br>
`파이썬 코드로, 내 랩탑에서 웹화면을 띄워주는 코드를 만들어주고, 상단에는 사용자 Input을 받고 아래는 send 버튼을 만들어줘` <br>
<img width="382" height="51" alt="image" src="https://github.com/user-attachments/assets/f45b1c23-6468-4181-8868-100ee1e66827" /><br>
<img width="392" height="431" alt="image" src="https://github.com/user-attachments/assets/be1ffc8f-dff6-420b-95bc-ca3bfef24826" /> <br>

### 1-3. 프로젝트 워크스페이스 생성
- 가이드 해주는대로 Create Workspace를 클릭합니다. <br>
(파일 및 디렉토리 구조는 다를수 있으며, Copilot Chat과 질문/답변하며 개별 파일을 수동으로 생성할수도 있습니다)
- 신규 프로젝트로 사용될 폴더를 선택해주시거나, 또는 적절한 위치에 "my-web-app" 새로 생성합니다. <br>
<img width="471" height="183" alt="image" src="https://github.com/user-attachments/assets/a54bb6c3-f6b6-4e55-8d9d-39ce97ba32f2" /> <br>
- 이후, 지정한 Workspace의 구조로 필요한 파일들도 함께 만들어진것을 확인합니다. <br>
app.py, index.html등 <br>
<img width="264" height="374" alt="image" src="https://github.com/user-attachments/assets/1de6cb26-4250-49c7-90d6-e92250d9ccc8" /> <br>

### 1-4. 앱 실행 및 문제 해결
- app.py를 열어보고, 실행해봅니다.<br>
<img width="910" height="386" alt="image" src="https://github.com/user-attachments/assets/54cb6613-9260-4ffe-9734-dfb7860258ef" /> <br>
- 유사한 다른 에러가 발생했다면 필요한 조치를 Copilot Chat에 에러를 넣고 물어봅니다. <br>
이미지를 캡쳐하여 Chat에 붙여넣어도 됩니다<br>
<img width="560" height="242" alt="image" src="https://github.com/user-attachments/assets/99c9b487-c42b-40b9-8a34-12ff4923d1c5" /><br>
<img width="383" height="325" alt="image" src="https://github.com/user-attachments/assets/6c761286-addb-45a2-8deb-bc39842ac0ee" /> <br>
<img width="552" height="198" alt="image" src="https://github.com/user-attachments/assets/3cb241b0-ba38-4235-ad2b-e6d6b7442d4d" /> <br>
- Error Fix 후에 다시 파이선을 수행합니다. <br>
<img width="550" height="218" alt="image" src="https://github.com/user-attachments/assets/a569cc7c-716d-477e-91ba-15a3667890de" /> <br>
- 정상 동작되면서 로컬에 웹이 기동됩니다. Ctrl누른 후 URL을 클릭합니다. <br>
<img width="820" height="287" alt="image" src="https://github.com/user-attachments/assets/6f76f922-0480-4278-b880-38b11912b167" /> <br>

## 2단계: LLM (ChatGPT) 연동하기
### 2-1. LLM 기능 추가 요청
- Copilot Chat에 추가 보완하고자 하는 내용을 추가합니다. <br>
`예) 사용자의 Input로 부터 값을 받아서, 이 값을 Azure openAI의 gpt4.1 로 보내고 , 나온 결과를 화면 상단에 출력해주도록 코드를 추가하고 싶어. 코드는 최소한만 수정하고 간단하게 알려줘`<br>
<img width="365" height="474" alt="image" src="https://github.com/user-attachments/assets/489de208-59f9-4fc6-b7db-38c5e79142d5" /><br>
> 참고) 아래 코드 가이드 순서는 개인마다 다를수 있으며, LLM에서 사용되는 gpt등 주요 API 키는 `Task3/env.txt` 를 사용하시면 됩니다<br>
- 코파일럿 챗의 가이드 대로 바이브코딩을 해 나갑니다. 

### 2-2. 필요한 라이브러리 및 환경변수 설정
필요한 Python 라이브러리를 설치. <br>
<img width="380" height="73" alt="image" src="https://github.com/user-attachments/assets/79fd4772-a1f1-435a-9ea6-9bfeda4b5b92" /><br>
<img width="405" height="137" alt="image" src="https://github.com/user-attachments/assets/3ff4629b-31c2-4509-af20-8f7e92437c0b" /><br>
- Azure OpenAI API정보등을 담을 .env 파일을 생성합니다. <br>
<img width="602" height="128" alt="image" src="https://github.com/user-attachments/assets/91539831-ec72-41c9-abeb-140aecedb8ee" /><br>
<img width="269" height="284" alt="image" src="https://github.com/user-attachments/assets/96fefc83-cc3e-4a95-9e8a-605364ca8b65" /><br>
`AZURE_OPENAI_ENDPOINT="https://yb-kor1.cognitiveservices.azure.com/"`<br>
`AZURE_OPENAI_API_KEY="<AZURE_OPENAI_API_KEY>"`<br>
`AZURE_OPENAI_DEPLOYMENT="gpt-4.1-mini"`<br>
`api_version = "2024-12-01-preview"`<br>

- app.py 코드 수정 버튼으로 적용해줍니다. <br>
<img width="368" height="335" alt="image" src="https://github.com/user-attachments/assets/9f9ef021-deec-401f-af49-671cdcd8aa15" /><br>
<img width="653" height="690" alt="image" src="https://github.com/user-attachments/assets/9f589e3a-a74d-4653-a603-f024b0aaf6ea" /> <br>
gpt API 버전이 맞지 않는다면 맞게 수정합니다. `api_version = "2024-12-01-preview"`
- html 파일도 마찬가지로, 수정 버튼으로 적용해 줍니다.<br>
<img width="586" height="286" alt="image" src="https://github.com/user-attachments/assets/ebbbbde7-28fb-4c18-99b0-7483edb6e058" /><br>

### 2-4. 코드 적용 및 테스트
- 이제 app.py 로 파이선을 실행합니다. <br>
<img width="42" height="27" alt="image" src="https://github.com/user-attachments/assets/c8c3ca9e-f2ff-4adc-8a86-6ac534a29cc2" /><br>
- output 결과창을 통해 URL 클릭 (Ctrl) <br>
<img width="545" height="212" alt="image" src="https://github.com/user-attachments/assets/afcb5410-1030-4034-b473-ae737a38521a" /><br>
- gpt를 통한 웹 채팅 서비스가 기동됩니다. <br>
<img width="577" height="373" alt="image" src="https://github.com/user-attachments/assets/5e2987c8-e7f2-4616-9d4c-5be8058cf59a" /> <br>

## 3단계 : AI 음성 인식 서비스 추가
### 3-1. 음성 인식 기능 요청
- Copilot Chat에 음성인식 기능을 추가해 달라고 요청합니다.<br>
`자 이제, App에 음성인식 기능을 붙이려고해. 기존 코드에 변경을 최소화하고, 최대한 간단하게 코드 수정할 부분을 위주로 알려줘.
먼저, 사용자 Input Text 우측에 마이크 버튼을 추가해주고, 누르면 사용자의 음성을 Input으로 받아서 Azure의 Speech to Text API로 넘겨주고, Text 결과를 Input 에 적어준다`<br>
<img width="391" height="607" alt="image" src="https://github.com/user-attachments/assets/d44f0c71-9631-49ba-9ee5-ea31bfc8336a" /><br>
- 가이드에 따라 코드를 하나씩 수정해봅니다. <br>

### 3-2. 음성 서비스 설정
- 먼저 필요한 Python 패키지를 설치합니다. <br>
<img width="381" height="66" alt="image" src="https://github.com/user-attachments/assets/70e4b60e-c924-43b3-b025-9ffee6f1fdcb" /><br>
<img width="307" height="136" alt="image" src="https://github.com/user-attachments/assets/83d7c3e0-9866-4db5-8b55-6de44a812544" /><br>
- .env 파일에 음성서비스 API키를 추가합니다. <br>
<img width="386" height="133" alt="image" src="https://github.com/user-attachments/assets/e0da1201-1323-4a5d-9c3a-4ad548ce0406" /><br>
<img width="732" height="363" alt="image" src="https://github.com/user-attachments/assets/8cd76c04-1b30-4c8f-8574-c92f896e8672" /><br>
`AZURE_SPEECH_KEY="<AZURE_SPEECH_KEY>"`<br>
`AZURE_SPEECH_REGION="koreacentral"`<br>
- Copilot의 가이드 대로 질문/답변을 반복해 나가면서 최종적으로 app.py 파일을 완성해보고, 파이썬 파일을 수행해봅니다. <br>
<img width="550" height="202" alt="image" src="https://github.com/user-attachments/assets/20a0e25d-4b4e-4765-9940-fb39cc0938b2" /><br>
<img width="548" height="384" alt="image" src="https://github.com/user-attachments/assets/e4d00d05-6956-461a-bdf0-a7ec94b6834c" /><br>
마이크를 통해 음성이 정상적으로 타이핑되었다면 성공입니다. 
<br>

### 3-3. 음성 출력 기능 추가
- 이제 Text 결과도 음성으로 함께 출력하는 기능을 붙여봅니다.<br>
Copilot Chat에 다음과 같이 요청해봅니다.<br>
`자 이제, 출력된 Text를 Speech로 목소리로도 출력하는 것을 추가해줘`<br>
<img width="279" height="580" alt="image" src="https://github.com/user-attachments/assets/b9efec27-dd4d-48d9-8250-2e8cbf08148f" /><br>
- 질문의 답변이 텍스트 + 음성으로 함께 나온다면 성공적으로 완료 되었습니다 .<br>

### 3-4. 음성 커스터마이징 (추가 미션)
- (참고) Azure에서는 다양한 한국어 음성을 지원하고 있고, 다양한 언어를 읽을수 있습니다. 추가 미션으로 목소리를 다르게 바꿔달라고 요청해봅니다.
<img width="278" height="600" alt="image" src="https://github.com/user-attachments/assets/5a6d784e-42be-4b02-b7d8-d7dc6932697e" /><br>


## 4단계: Copilot Chat Agent 모드 실습
### 4-1. Agent 모드 시작
- 새로운 Copilot Chat창을 열어 봅니다.(이미 열려있는 Chat창이라면, 상단의 +버튼으로 새롭게 시작)<br>
- Chat모드는 **Agent**를 선택합니다.<br>
<img width="187" height="411" alt="image" src="https://github.com/user-attachments/assets/1896e79b-40d4-4214-8319-2fcd004dab78" /><br>

### 4-2. Agent 모드 특징
- Agent 모드는 보다 **복잡한 작업**을 **자율적으로 수행**할 수 있습니다. AI는 작업이 완료될 때까지 코드를 단계별로 실행하도록 가이드해줍니다.<br>
- 아주 간단하게 Agent 모드를 동작시켜 봅시다.<br>

### 4-3. Agent 모드로 웹앱 생성
- 채팅창에 아래 내용을 입력해봅니다.<br>
`파이썬으로 간단한 챗봇 웹어플리케이션을 만들어줘. 사용자 입력을 text로 받고 챗봇의 결과를 출력해주는 화면을 만들어줘. 디자인은 모던하게.`<br>
<img width="881" height="576" alt="image" src="https://github.com/user-attachments/assets/eb790ecc-6551-47e1-bc87-e0555df21c32" /><br>

### 4-4. 생성된 파일 확인 및 실행
- Agent 모드는 사용자가 허용하면, 필요한 폴더 파일들을 자동으로 생성합니다. 이후에 만들어진 파일들을 유지할지 취소할지를 결정하게 됩니다. **Keep**을 선택!<br>
<img width="370" height="217" alt="image" src="https://github.com/user-attachments/assets/70831584-7a2d-4b45-944c-aa84e5b4d623" /><br>
- app.py를 실행하여 로컬에서 웹서비스를 띄워봅니다.<br>
<img width="538" height="208" alt="image" src="https://github.com/user-attachments/assets/b08b1694-e32e-4100-d7d-0850d2c646f9" /><br>
- 정상적으로 접속되는 것을 확인할 수 있습니다.<br>
<img width="457" height="476" alt="image" src="https://github.com/user-attachments/assets/8b524316-cff9-45ca-abee-bcf9171ad113" /><br>

### 4-5. Agent 모드와 Ask 모드 비교
> **💡 참고사항**  
> - **Ask 모드**: 단계별 질문과 답변을 통해 사용자가 직접 코드를 수정하고 적용
> - **Agent 모드**: AI가 자율적으로 전체 작업을 계획하고 파일을 생성하여 완성된 결과물 제공
> 
> 복잡한 프로젝트 시작 시에는 Agent 모드가, 기존 코드 수정이나 세부 조정에는 Ask 모드가 더 적합합니다.
<br>

Task3을 모두 완료 하였습니다.<br><br>





















  
