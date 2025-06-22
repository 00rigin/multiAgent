# 🤖 멀티 에이전트 채팅 시스템

LangChain과 LangGraph를 사용한 멀티 에이전트 채팅 시스템입니다. 일반적인 대화, 검색, 일정 관리 기능을 제공합니다.

## 🚀 주요 기능

### 🤖 에이전트
- **Chat Agent**: 일반적인 대화 및 질문 답변
- **Researcher Agent**: 네이버 검색을 통한 정보 조사
- **Calender Agent**: 캘린더 일정 등록/조회/수정/삭제
- **Mail Agent**: 이메일 전송
- **Supervisor Agent**: 에이전트 할당

### 💾 메모리 시스템
- 세션별 채팅 히스토리 유지
- 대화 컨텍스트 기억

### 🎨 사용자 인터페이스
- **API**: FastAPI 기반 REST API
- **Web UI**: Streamlit 기반 채팅 인터페이스

## 🎯 신경쓴 부분

### 1. **프롬프트 중앙 관리**
- 모든 에이전트의 프롬프트를 `app/config/prompts.py`에서 한 곳에 관리
- 프롬프트 수정 시 코드 변경 없이 한 곳만 수정하면 모든 에이전트에 적용
- 일관성 있는 프롬프트 스타일과 유지보수성 향상
- 프롬프트 엔지니어와의 협업을 위한 별도 파일로서 관리

### 2. **인터페이스 기반 Agent Tool 확장성**
- 각 에이전트가 사용하는 도구들을 인터페이스로 설계
     - `CalendarInterface`
     - `MailInterface`
     - `SearchInterface`
- Interface의 구현체를 변경할 수 있게 하여 자유도 향상
     - `CalendarInterface` <- `KaKaoCalendarComponent`
     - `MailInterface` <- `GamilComponent`
     - `SearchInterface` <- `NaverSearchComponent`
- 새로운 서비스 추가 시 기존 코드 변경 없이 인터페이스 구현만으로 확장

### 3. **LLM 가드레일 시스템**
- `app/config/guardrail_patterns.py`에서 모든 가드레일 패턴을 중앙 관리
- **그래프 레벨 가드레일**: 모든 입력과 출력이 자동으로 검사됨
- 금지 키워드, 스팸 패턴, 경고 키워드 자동 감지
- 안전하지 않은 요청에 대한 표준화된 거부 응답

#### 가드레일 기능:
- **입력 검증**: 사용자 입력의 개인정보, 불법/유해 내용, 폭력/차별 표현 감지
- **출력 검증**: AI 응답의 안전성 검사 및 차단
- **이메일 특화**: 스팸/피싱 방지, 대량 발송 제한, 이메일 주소 검증
- **캘린더 특화**: 일정 제목과 설명의 안전성 검사
- **확장 가능**: 사용자 정의 패턴 추가 가능

#### 그래프 레벨 가드레일 흐름:
```
사용자 입력 → input_guardrail → supervisor → 에이전트 → output_guardrail → supervisor → 응답
     ↓              ↓              ↓           ↓           ↓
  안전성 검사    차단 시 응답      라우팅       처리      출력 검사
```

## 📋 설치 및 실행

### Python3.10

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

## 📁 프로젝트 구조

```
multiAgent/
│  .env
│  .gitignore
│  README.md
│  requirements.txt
│  run_streamlit.py
│  test_main.http
│
├─app
│  │  main.py
│  │  MessageRequest.py
│  │  streamlit_chat.py
│  ├─api
│  │  └─v1
│  │      └─chat.py
│  ├─component
│  │  ├─calendar
│  │  │  │  CalendarInterface.py
│  │  │  └─kakaoCalendar
│  │  │      └─KaKaoCalendarComponent.py
│  │  ├─mail
│  │  │  │  MailInterface.py
│  │  │  └─gmail
│  │  │      └─GmailComponent.py
│  │  ├─search
│  │  │  │  SearchInterface.py
│  │  │  └─naver
│  │  │      └─NaverSearchComponent.py
│  ├─config
│  │  │  ai.py
│  │  │  guardrail_patterns.py
│  │  │  prompts.py
│  │  │  settings.py
│  ├─domain
│  │  ├─agents
│  │  │  ├─advisor
│  │  │  │  └─ChatAgent.py
│  │  │  ├─calenderMaker
│  │  │  │  └─CalenderAgent.py
│  │  │  ├─mailAgent
│  │  │  │  └─MailAgent.py
│  │  │  ├─researcher
│  │  │  │  └─SearchAgent.py
│  │  │  ├─supervisor
│  │  │  │  └─supervisor.py
│  │  │  └─AgentType.py
│  │  ├─gaurdrails
│  │  │  ├─guardrailNode.py
│  │  │  └─guardrails.py
│  │  ├─graph
│  │  │  ├─agentNode.py
│  │  │  ├─AgentState.py
│  │  │  ├─memory.py
│  │  │  ├─setup.py
│  │  │  └─TravelChatGraph.py
│
├─resources
│      credentials.json
│      token.json
```

## 동작 결과
![chat1.png](statics/chat1.png)
![chat2.png](statics/chat2.png)
![chat3.png](statics/chat3.png)
![mail.png](statics/mail.png)


## 사용 개발 도구
### PyCharm
기본 적인 작업을 수행할 때 사용.
### Cursor
프론트 화면 구현시 100% 사용.
서버 작업시 50% 사용.
예시를 하나 만들고 이를 따라할 수 있도록 지도하여 개발을 수행함.
ex) Agent 하나 만들고 스타일 따라하여 다른 Agent 만들기
ex) Tool의 interface-구현체 분리 작업후 다른 컴포넌트도 똑같이 분리하기 등.
