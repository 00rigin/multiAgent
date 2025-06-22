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

## 🎯 신경쓴 부분

### 1. **프롬프트 중앙 관리**
- 모든 에이전트의 프롬프트를 `app/config/prompts.py`에서 한 곳에 관리
- 프롬프트 수정 시 코드 변경 없이 한 곳만 수정하면 모든 에이전트에 적용
- 일관성 있는 프롬프트 스타일과 유지보수성 향상

### 2. **인터페이스 기반 확장성**
- 각 에이전트가 사용하는 도구들을 인터페이스로 설계
- `CalendarInterface`, `MailInterface`, `SearchInterface` 등을 통해 구현체 교체 가능
- 새로운 서비스 추가 시 기존 코드 변경 없이 인터페이스 구현만으로 확장

### 3. **LLM 가드레일 시스템**
- `app/config/guardrails.py`에서 안전성 검증 시스템 제공
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
사용자 입력 → input_guardrail → supervisor → 에이전트 → output_guardrail → 응답
     ↓              ↓              ↓           ↓           ↓
  안전성 검사    차단 시 응답        라우팅        처리      출력 검사
```

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
│  │  │  └─kakaoCalendar
│  │  │     └─KaKaoCalendarComponent.py
│  │  ├─mail
│  │  │  ├─gmail
│  │  │  │  └─GmailComponent.py
│  │  │  └─MailInterface.py
│  │  └─search
│  │     ├─naver
│  │     │  └─NaverSearchComponent.py
│  │     └─SearchInterface.py
│  ├─config
│  │  ├─ai.py
│  │  ├─settings.py
│  │  ├─prompts.py
│  │  └─guardrails.py          # 🛡️ 가드레일 시스템
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
│  │  │  └─supervisor
│  │  │     └─supervisor.py
│  │  └─graph
│  │     ├─agentNode.py
│  │     ├─AgentState.py
│  │     ├─memory.py
│  │     ├─setup.py
│  │     └─TravelChatGraph.py
├─resources
├─statics
│  ├─chat1.png
│  ├─chat2.png
│  ├─chat3.png
│  └─mail.png
```

## 📝 프롬프트 관리 시스템 사용법

### 기본 사용법
```python
from app.config.prompts import get_prompt

# 각 에이전트별로 프롬프트 가져오기
chat_prompt = get_prompt('chat')
search_prompt = get_prompt('search')
calendar_prompt = get_prompt('calendar')
mail_prompt = get_prompt('mail')
supervisor_prompt = get_prompt('supervisor')
```

### 에이전트에서 사용
```python
# ChatAgent 예시
from app.config.prompts import get_prompt

class ChatAgent:
    def __init__(self, llm=None):
        self.llm = llm or openai_chat
        
        # 프롬프트 가져오기
        system_prompt = get_prompt('chat')
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
```

### 프롬프트 수정
프롬프트를 수정하려면 `app/config/prompts.py` 파일에서 해당 프롬프트를 직접 편집하면 됩니다:

```python
# app/config/prompts.py
CHAT_PROMPT = """당신은 친근하고 도움이 되는 AI 어시스턴트입니다.
# 여기서 프롬프트 내용을 수정
"""
```

## 🔧 인터페이스 기반 확장 예시

### 새로운 캘린더 서비스 추가
```python
# GoogleCalendarComponent.py (새로운 구현체)
from app.component.calendar.CalendarInterface import CalendarInterface

class GoogleCalendarComponent(CalendarInterface):
    def create_event(self, title: str, description: str, start_at: str, end_at: str):
        # Google Calendar API 구현
        pass

# CalenderAgent에서 사용
calendar_component = GoogleCalendarComponent()  # KakaoCalendar 대신 사용
calender_agent = CalenderAgent(calendar_component=calendar_component)
```

### 새로운 검색 서비스 추가
```python
# GoogleSearchComponent.py (새로운 구현체)
from app.component.search.SearchInterface import SearchInterface

class GoogleSearchComponent(SearchInterface):
    def search(self, query: str):
        # Google Search API 구현
        pass

# SearchAgent에서 사용
search_component = GoogleSearchComponent()  # NaverSearch 대신 사용
search_agent = SearchAgent(search_component=search_component)
```

## 🔧 프롬프트 관리 시스템의 장점

### 1. **중앙화된 관리**
- 모든 에이전트의 프롬프트가 `app/config/prompts.py`에 저장
- 프롬프트 수정 시 한 곳만 변경하면 모든 에이전트에 적용
- 일관성 있는 프롬프트 스타일 유지

### 2. **단순한 구조**
- 복잡한 클래스나 설정 없이 단순한 함수 하나로 관리
- `get_prompt(agent_type)` 함수로 쉽게 프롬프트 가져오기
- 코드 변경 없이 프롬프트만 수정 가능

### 3. **유지보수성**
- 프롬프트 전문가와 개발자 간 협업 용이
- 프롬프트 변경 이력 추적 가능
- 새로운 에이전트 추가 시 기존 패턴 재사용

### 4. **확장성**
- 필요시 프롬프트 변형이나 설정 파일 지원 추가 가능
- A/B 테스트를 위한 프롬프트 변형 시스템 확장 가능

## 동작 결과
![chat1.png](statics/chat1.png)
![chat2.png](statics/chat2.png)
![chat3.png](statics/chat3.png)
![mail.png](statics/mail.png)