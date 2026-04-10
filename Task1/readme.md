# Task 1: 간단한 함수 코드 작성하기 (Code 완성 기능 사용)

## Use case: 
- GitHub Copilot를 활용하여 간단한 함수와 테스트 코드를 제안받습니다. 이를 통해, GitHub Copilot이 기본적인 기능을 익히고, 어떠한 방식으로 일반적인 코딩 작업을 지원하는지 확인할 수 있습니다.

## 목표:
- 주석을 활용하여, 간단한 함수 (factorial, is_prime)를 코드완성 기능으로 작성합니다. 
- 작성한 함수에 대한 테스트 코드를 작성합니다.
- GitHub Copilot Log를 확인하여, 오픈소스와 매치되는 코드인 경우 레퍼런스 정보를 확인합니다. 
- VS Code의 Copilot 메뉴에 관한 기본적인 설정들을 변경해 봅니다.

## Step 1 : 기본 함수 작성
### 1.1 작업 환경 설정
- VS Code를 실행하고, 실습을 진행할 디렉토리를 엽니다<br>
(좌측 상단의 File > Open Folder)<br>
<img width="352" height="299" alt="image" src="https://github.com/user-attachments/assets/0db4f3a0-4876-457f-98ce-cdfbbefd90a2" /><br>
작업 디렉토리로 사용할 폴더를 생성합니다.(1107-ghcp)<br>
<img width="855" height="484" alt="image" src="https://github.com/user-attachments/assets/fb4f0a2b-a5b2-4ea0-92c8-393056d3c5df" /><br>
### 1.2 파이썬 파일 생성 및 함수 작성
- 이제 파이선 코드를 만들어 봅니다.(실습은 파이썬으로 진행)<br>
좌측 상단의 Explorer에 New File 아이콘을 눌러 파일을 생성합니다. 팩토리얼 함수를 만들것이므로 이름은 factorial.py 로 생성합니다<br>
  <img width="295" height="269" alt="image" src="https://github.com/user-attachments/assets/29e8a59b-9bec-4c50-a225-ac22f7f78497" />


- 우측의 코드입력창이 나타납니다. <br>
생성할 함수를 아래의 주석으로 입력후, 엔터를 칩니다.<br>
  `# 팩토리얼 함수 `<br>
<img width="242" height="104" alt="image" src="https://github.com/user-attachments/assets/874f68a8-0a1f-4dec-ba0f-0b1fbec31a21" /> <br>
잠시후 Github Copilot이 주석의 내용을 참고하여 함수를 제안해줍니다.<br>
만약, 아무 반응이 없다면 스페이스 또는 . 을 눌러서 Copilot이 깨어나도록 해주세요<br>

- 회색으로 제안된 코드를 확인하고, Tab키를 눌러서 코드를 완성합니다.<br>
<img width="242" height="104" alt="image" src="https://github.com/user-attachments/assets/1825fce9-3a29-49c0-a560-6780d7d3241e" /><br>
첫번째 **Code 완성** 기능을 완료했습니다.<br><br>

### 1.3 Copilot Suggestions 기능 설정
이번에는 코드상에서 바로 제안해주는 Inline 방식 대신, 별도 창을 띄워서 코드 제안을 받는 Copilot Suggestions기능을 살펴보겠습니다.<br>
- 설정 창으로 이동합니다. `Ctrl + Shift + P`를 누르면 상단에 명령 팔레트가 열립니다.<br>
'`GitHub Copilot: Open Completions Panel`' 를 입력하면 해당 메뉴 우측으로 설정(톱니바퀴 모양)을 눌러봅니다.<br>
<img width="535" height="199" alt="image" src="https://github.com/user-attachments/assets/440ec41c-0e76-495e-9038-d565f9be6bcc" /><br>
- 왼편의 '+' 버튼을 눌러 단축키를 설정해봅니다. 이미 설명해뒀었다면 연필모양을 눌러 단축키를 입력합니다. Ctrl+Enter 로 넣어주세요.<br>
<img width="417" height="72" alt="image" src="https://github.com/user-attachments/assets/9601fd87-b9f9-48ec-96e4-5651cb33b75b" /><br>
<img width="316" height="114" alt="image" src="https://github.com/user-attachments/assets/c248332f-8776-41f6-a507-496e1b4af0a3" /><br>
엔터를 눌러 저장합니다.<br>

### 1.4 소수 판별 함수 추가
- 잘 동작하는지를 살펴보겠습니다. factorial.py 코드로 돌아가서, 하단에 새로운 주석을 통해 소수를 판별하는 함수를 추가해보겠습니다.<br>
  `# 소수 판별 함수`<br>
  입력후 엔터를 치면 조금전 처럼 코드 추천이 나타납니다. <br>
  이때 코드를 수락하지 않은 상태에서 Ctrl + Enter를 눌러서 제안되는 리스트를 확인합니다.br>
  <img width="668" height="289" alt="image" src="https://github.com/user-attachments/assets/d415a422-5cea-41db-bb2b-39fc4d8629aa" /><br>
Accept Suggestions을 통해 코드에 반영합니다.<br>
- 파이썬 코드 정상 동작하는지 수행해봅니다.<br>
상단의 수행버튼을 눌러보면 파이썬 코드가 실행되고, 하단의 터미널에 결과가 표시됩니다.<br>
현재 출력은 없으며, 에러없이 수행되면 됩니다.<br>
<img width="636" height="358" alt="image" src="https://github.com/user-attachments/assets/cab1300f-d06c-49a6-af58-54a65d0968dc" /><br>

## Step 2 : Copilot Log 확인하기
- VS Code 하단 터미널 창 부분의 `OUTPUT` 탭으로 이동합니다.<br>
우측의 메뉴에서 항목을 `GitHub Copilot`, `GitHub Copilot Chat`이 나타나는것을 볼수 있습니다. Copilot 관련 로그는 여기서 각각 확인 가능합니다.<br>
<img width="700" height="201" alt="image" src="https://github.com/user-attachments/assets/eaea1b10-a087-448a-9a3a-c29527dc5a59" />


- GitHub Copilot 혹은 GitHub Copilot Chat 을 선택해 로그를 확인합니다. <br>
<img width="749" height="201" alt="image" src="https://github.com/user-attachments/assets/0540ccc8-4710-48f6-8a46-f376d4fd33e3" />
<img width="749" height="200" alt="image" src="https://github.com/user-attachments/assets/36f08e92-839a-4e3a-8b9d-78344423f86d" />

- 만약, 제안되는 코드가 오픈소스와 매칭되는 부분이 있다면, `GitHub Copilot Log(Code References)`에서 관련 로그를 볼 수 있습니다.<br>
- 다만, GitHub Copilot 관리자가 오픈소스 매칭되는 코드를 제안받지 않겠다고 설정하면, 로그를 볼 수 없습니다. <br>
아래는 예시이며, 매칭되는 내용이 있을시 아래처럼 표기됩니다.<br>
<img width="700" height="1168" alt="image" src="https://github.com/user-attachments/assets/2a829dd5-e75b-4a71-a5a5-9a744d2973f1" /><br>


## Step 3 : 우클릭 마우스 Copilot 메뉴 사용하기
### 3.1 테스트 코드 생성
- 소스코드를 선택후, 마우스 우클릭 버튼을 클릭하여, 'Generate Code' 메뉴의 **generate_test**를 선택합니다.<br>
<img width="500" height="558" alt="image" src="https://github.com/user-attachments/assets/777619a0-381d-4e24-b34a-ec0c867656c3" /> <br>
- 테스트 수행할수 있는 스크립트를 자동 생성해줍니다.<br>
<img width="700" height="415" alt="image" src="https://github.com/user-attachments/assets/7c0ebe1d-4253-4223-affa-bf6f56996fd5" /> <br>
-동작 정상 확인 <br>
<img width="700" height="707" alt="image" src="https://github.com/user-attachments/assets/a60d8769-29e9-4b6b-ad53-ed843dc618a6" /><br>

### 3.2 문서 생성
- 마우스 오른 버튼을 클릭하여 'Generate Code' 메뉴의 **generate_docs**를 선택합니다.<br>
주석이 생긴것을 확인하고 Accept! <br>
<img width="442" height="463" alt="image" src="https://github.com/user-attachments/assets/747e48fe-fa66-4fcf-a8dc-5068a2c5ae04" /> <br>



## Step 4 : 코드 완성 기능 동작 매커니즘 이해하기
### 4.1 컨텍스트 이해 방식
- Copilot은 코드 완성 기능을 제공하기 위해, **주석과 함수 이름을 기반으로** 컨텍스트를 이해합니다.<br>
- 또한, 현재 작성중인 파일의 커서 위치의 **전,후 데이터**와, 이 데이터와 유사한 데이터를 **오픈되어져 있는 주변의 탭**에서 찾아 컨텍스트를 이해합니다. (**Neighboring Tab**) <br>

### 4.2 Neighboring Tab 기법 테스트
- 코드 완성 기능에서의 Neighboring Tab 기법을 테스트하기 위해 아래 절차대로 실습합니다. 
- Task1 의 `/src` 디렉토리에 `url_tools.py`, `url.py` 파일이 있습니다. <br>
각각의 파일을 복사하여 내 워크스페이스에 새로운 파일로 각각 만듭니다.<br>
url.py<br>
<img width="605" height="243" alt="image" src="https://github.com/user-attachments/assets/15a09539-1f3e-4e1c-90ae-29758d735517" />  <br>
url_tools.py<br>
<img width="462" height="413" alt="image" src="https://github.com/user-attachments/assets/b74d77b7-6470-45ea-9758-351e9206fe77" /> <br>

- `url_utils.py` 파일은 오픈된 상태로 두고, `url.py` 파일의 마지막 라인에서 커버를 두고  Enter를 누르면 아래와 같이 url_tools.py의 함수가 제안됩니다.<br>   
<img width="642" height="370" alt="image" src="https://github.com/user-attachments/assets/3e71e41d-c92b-4b24-8a2d-2607a5c352e8" />



## Step 5 : VS Code의 Copilot 설정 메뉴
### 5.1 언어 설정 변경
- Copilot의 기본 언어를 한국어로 바꿔보겠습니다. <br>
VS Code에서 Ctrl + Shift + P를 눌러 명령 팔레트를 열고, 'preference'을 검색하여, `Preference: Open Settings (UI)`를 선택합니다.<br>
<img width="527" height="301" alt="image" src="https://github.com/user-attachments/assets/3b23d8ae-82c2-430c-8b77-3481cb5f6f94" /><br>

- 상단에서 검색어로 Copilot locale을 검색하고, 'ko'로 변경합니다.<br>
<img width="419" height="439" alt="image" src="https://github.com/user-attachments/assets/cefdec05-ec30-483b-92a2-2b79e4813373" /><br>
자동저장됩니다.<br>

### 5.2 NES(Next Edit Suggestion) 기능 설정
- Copilot이 코드를 제안시 앞뒤 문맥이 변경되었을때 연결된 뒤 코드도 연결해서 수정해주는 기능을 제공합니다. `NES(Next Edit Suggestion)` 기능을 활성화/비활성화 할수 있습니다.<br>
검색창에 `copilot next edit` 이라 입력하고, 활성화 기능을 조정할수 있습니다.<br>
Default는 Enable이 되어 있습니다<br>
<img width="672" height="282" alt="image" src="https://github.com/user-attachments/assets/4425799a-bd33-41dc-a9ef-3716ce78e163" /><br><br>

### 5.3 LLM 모델 변경
- Code 완성 기능에서 사용되는 LLM 기본 모델을 변경해 봅니다.<br>
- 상단의 Copilot 아이콘의 우측 아래화살표를 클릭하고, `Configure Code completion`을 선택합니다.<br>
<img width="662" height="186" alt="image" src="https://github.com/user-attachments/assets/8a3dc99c-4df5-477e-96cf-63026e795288" /><br>
'Change completion model'을 선택합니다.<br>
<img width="296" height="183" alt="image" src="https://github.com/user-attachments/assets/56c9f3e3-90ca-4b54-be34-bdd7ed6c6f44" /> <br>
- 모델을 변경할수 있습니다. (현재는 gpt4.1 모델이 보이며, 시점/권한에 따라 보이는 모델은 다를수 있습니다.) <br>
<img width="289" height="87" alt="image" src="https://github.com/user-attachments/assets/2428ed67-8542-4d8d-951e-d1ab01fbea4f" /><br>





- Reference : [VS Code Copilot settings reference 문서](https://code.visualstudio.com/docs/copilot/copilot-settings)


## 참고 : Copilot 관련 기술 지원
- [GitHub 도움말 : Troubleshoot GitHub Copilot 문서 참조](https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/troubleshoot)

- (기업 관리자)각종 에러로그, 화면 캡쳐 등을 첨부하여 GitHub 글로벌 Support에 기술지원 요청/문의할 수 있습니다. <br>
  - [GitHub Support](https://support.github.com)

## 지식 확인
- GitHub Copilot의 코드 완성 기능
- 코드완성 기능의 모델 선택
- GitHub Copilot의 코드 완성 기능의 컨텍스트
- VS Code의 Copilot 설정 메뉴



