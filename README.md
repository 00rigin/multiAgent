# 🤖 멀티 에이전트 채팅 시스템

LangChain과 LangGraph를 사용한 멀티 에이전트 채팅 시스템입니다. 일반적인 대화, 검색, 일정 관리 기능을 제공합니다.

## 🚀 주요 기능

### 🤖 에이전트
- **Chat Agent**: 일반적인 대화 및 질문 답변
- **Researcher Agent**: 네이버 검색을 통한 정보 조사
- **Calender Agent**: 카카오 캘린더 일정 등록
- **Mail Agent**: 이메일 전송
- **Supervisor Agent**: 에이전트 할당

### 💾 메모리 시스템
- 세션별 채팅 히스토리 유지
- 대화 컨텍스트 기억

### 🎨 사용자 인터페이스
- **API**: FastAPI 기반 REST API
- **Web UI**: Streamlit 기반 채팅 인터페이스

## 📋 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 다음 정보를 입력하세요:
```env
OPENAI_KEY = your-openai-api-key
NAVER_CLIENT_ID= your-naver-client-id
NAVER_CLIENT_SECRET= your-naver-client-secret
KAKAO_KEY = your-kakao-authorization-token
GOOGLE_CREDENTIAL_PATH = ./resources/credentials.json // Google API 인증 정보 파일 경로(실제 파일이 필요합니다.)
GMAIL_TOKEN_PATH = ./resources/token.json // Gmail API 토큰 파일 경로 (위 cred를 바탕으로 생성되는 위치입니다.)
```

### 3. API 서버 실행
```bash
python -m uvicorn app.main:app
```
API 서버가 `http://localhost:8000`에서 실행됩니다.

### 4. Streamlit 채팅 앱 실행
```bash
python run_streamlit.py
```
채팅 앱이 `http://localhost:8501`에서 실행됩니다.

## 🏗️ 프로젝트 구성

```
multiAgent/
│  .env
│  .gitignore
│  README.md
│  requirements.txt
│  run_streamlit.py
├─app
│  │  main.py
│  │  MessageRequest.py
│  │  streamlit_chat.py
│  ├─component
│  │  ├─calendar
│  │  │  │  CalendarInterface.py
│  │  │  ├─KakaoCalendar
│  │  │  │  │  KaKaoCalendarComponent.py
│  │  ├─kakaoTalk
│  │  │      KakaoTalkComponent.py
│  │  ├─mail
│  │  │  │  MailInterface.py
│  │  │  │
│  │  │  ├─gmail
│  │  │  │  │  GmailComponent.py
│  ├─config
│  │  │  ai.py
│  │  │  settings.py
│  │  │
│  ├─domain
│  │  ├─agents
│  │  │  ├─advisor
│  │  │  │  │  ChatAgent.py
│  │  │  ├─calenderMaker
│  │  │  │  │  CalenderAgent.py
│  │  │  ├─mailAgent
│  │  │  │  │  MailAgent.py
│  │  │  ├─researcher
│  │  │  │  │  NaverSearchAPIWrapper.py
│  │  │  │  │  SearchAgent.py
│  │  │  ├─supervisor
│  │  │  │  │  supervisor.py
│  │  ├─graph
│  │  │  │  agentNode.py
│  │  │  │  AgentState.py
│  │  │  │  memory.py
│  │  │  │  setup.py
│  │  │  │  TravelChatGraph.py
└─resources
        credentials.json
```
## 동작 결과
![chat1.png](statics/chat1.png)
![chat2.png](statics/chat2.png)
![chat3.png](statics/chat3.png)