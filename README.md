# 🤖 멀티 에이전트 채팅 시스템

LangChain과 LangGraph를 사용한 멀티 에이전트 채팅 시스템입니다. 일반적인 대화, 검색, 일정 관리 기능을 제공합니다.

## 🚀 주요 기능

### 🤖 에이전트
- **Chat Agent**: 일반적인 대화 및 질문 답변
- **Researcher Agent**: 네이버 검색을 통한 정보 조사
- **Calender Agent**: 카카오 캘린더 일정 등록

### 💾 메모리 시스템
- 세션별 채팅 히스토리 유지
- 대화 컨텍스트 기억
- 히스토리 조회/삭제 기능

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
OPENAI_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
KAKAO_KEY=your_kakao_api_key
```

### 3. API 서버 실행
```bash
python -m uvicorn app.main:app --reload --log-level debug
```
API 서버가 `http://localhost:8000`에서 실행됩니다.

### 4. Streamlit 채팅 앱 실행
```bash
python run_streamlit.py
```
또는
```bash
streamlit run app/streamlit_chat.py
```
채팅 앱이 `http://localhost:8501`에서 실행됩니다.

## 🔧 API 사용법

### 채팅
```bash
POST /chat
{
    "message": "안녕하세요!",
    "session_id": "optional-session-id"
}
```

### 히스토리 조회
```bash
GET /chat/history/{session_id}
```

### 히스토리 삭제
```bash
DELETE /chat/history/{session_id}
```

### 통계 조회
```bash
GET /chat/stats
```

## 🎯 사용 예시

### 일반적인 대화
```
사용자: "안녕하세요! 오늘 날씨가 어때요?"
AI: "안녕하세요! 오늘 날씨에 대해 말씀드리겠습니다..."
```

### 검색 요청
```
사용자: "서울 날씨에 대해 검색해주세요"
AI: "네이버에서 서울 날씨 정보를 검색해드리겠습니다..."
```

### 일정 관리
```
사용자: "내일 오후 2시에 회의 일정을 등록해주세요"
AI: "카카오 캘린더에 회의 일정을 등록하겠습니다..."
```

## 🏗️ 프로젝트 구조

```
multiAgent/
├── app/
│   ├── config/           # 설정 파일
│   │   └── graph/        # LangGraph 설정
│   ├── main.py           # FastAPI 서버
│   └── streamlit_chat.py # Streamlit UI
├── requirements.txt
├── run_streamlit.py
└── README.md
```

## 🔍 디버깅

### 로그 확인
- API 서버: `--log-level debug` 옵션으로 상세 로그 확인
- Streamlit: 브라우저 개발자 도구에서 콘솔 로그 확인

### 일반적인 문제
1. **API 연결 오류**: API 서버가 실행 중인지 확인
2. **에이전트 오류**: 환경 변수가 올바르게 설정되었는지 확인
3. **메모리 오류**: 세션 ID가 올바른지 확인

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🙏 감사의 말

- LangChain 팀
- Streamlit 팀
- FastAPI 팀 