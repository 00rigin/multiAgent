import streamlit as st
import requests
import json
import uuid
from datetime import datetime
import time

# 페이지 설정
st.set_page_config(
    page_title="멀티 에이전트 채팅",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .ai-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .message-time {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .session-info {
        background-color: #f0f0f0;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin-bottom: 1rem;
    }
    .stButton > button {
        width: 100%;
    }
    .input-hint {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
        text-align: center;
    }
    .input-container {
        border: 2px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        background-color: #fafafa;
        margin-top: 1rem;
    }
    .keyboard-shortcuts {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.3rem;
        padding: 0.5rem;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# API 설정
API_BASE_URL = "http://localhost:8000"

def send_message(message, session_id=None):
    """API로 메시지를 전송합니다."""
    try:
        payload = {
            "message": message,
            "session_id": session_id
        }
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API 오류: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"연결 오류: {str(e)}"}

def get_chat_history(session_id):
    """채팅 히스토리를 가져옵니다."""
    try:
        response = requests.get(f"{API_BASE_URL}/chat/history/{session_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return {"messages": []}
    except:
        return {"messages": []}

def clear_chat_history(session_id):
    """채팅 히스토리를 삭제합니다."""
    try:
        response = requests.delete(f"{API_BASE_URL}/chat/history/{session_id}")
        return response.status_code == 200
    except:
        return False

def process_message(message_input):
    """메시지를 처리하는 함수"""
    if message_input.strip():
        st.session_state.is_loading = True
        
        # 사용자 메시지를 히스토리에 추가
        user_message = {
            "type": "human",
            "content": message_input,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.chat_history.append(user_message)
        
        # API 호출
        response = send_message(message_input, st.session_state.session_id)
        
        if "error" not in response:
            # AI 응답을 히스토리에 추가
            ai_message = {
                "type": "ai",
                "content": response["response"],
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.chat_history.append(ai_message)
        else:
            # 오류 메시지 추가
            error_message = {
                "type": "ai",
                "content": f"오류: {response['error']}",
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.chat_history.append(error_message)
        
        st.rerun()

# 세션 상태 초기화
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False
if "pending_message" not in st.session_state:
    st.session_state.pending_message = None
if "clear_input_flag" not in st.session_state:
    st.session_state.clear_input_flag = False

# 사이드바
with st.sidebar:
    st.title("🤖 멀티 에이전트 채팅")
    
    # 세션 관리
    st.subheader("📋 세션 관리")
    
    # 새 세션 생성
    if st.button("🆕 새 세션"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.rerun()
    
    # 현재 세션 ID 표시
    st.text_area("현재 세션 ID", st.session_state.session_id, height=100)
    
    # 세션 ID 입력
    new_session_id = st.text_input("세션 ID 입력")
    if st.button("세션 변경") and new_session_id:
        st.session_state.session_id = new_session_id
        st.session_state.chat_history = []
        st.rerun()
    
    st.divider()
    
    # 히스토리 관리
    st.subheader("🗂️ 히스토리 관리")
    
    if st.button("📥 히스토리 불러오기"):
        history = get_chat_history(st.session_state.session_id)
        if "messages" in history:
            st.session_state.chat_history = history["messages"]
            st.rerun()
    
    if st.button("🗑️ 히스토리 삭제"):
        if clear_chat_history(st.session_state.session_id):
            st.session_state.chat_history = []
            st.rerun()
            st.success("히스토리가 삭제되었습니다!")
        else:
            st.error("히스토리 삭제에 실패했습니다.")
    
    st.divider()
    
    # 에이전트 정보
    st.subheader("🤖 에이전트 정보")
    st.markdown("""
    - **Chat**: 일반적인 대화
    - **Researcher**: 검색 및 정보 조사
    - **Calender**: 일정 관리
    """)

# 메인 채팅 영역
st.title("💬 멀티 에이전트 채팅")

# 세션 정보 표시
with st.container():
    st.markdown(f"""
    <div class="session-info">
        <strong>현재 세션:</strong> {st.session_state.session_id[:8]}...
    </div>
    """, unsafe_allow_html=True)

# 채팅 히스토리 표시
chat_container = st.container()

with chat_container:
    for message in st.session_state.chat_history:
        if message["type"] == "human":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 사용자:</strong><br>
                {message["content"]}
                <div class="message-time">사용자 메시지</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message ai-message">
                <strong>🤖 AI:</strong><br>
                {message["content"]}
                <div class="message-time">AI 응답</div>
            </div>
            """, unsafe_allow_html=True)

# 로딩 표시
if st.session_state.is_loading and st.session_state.pending_message:
    with st.spinner("🤖 AI가 응답을 생성하고 있습니다..."):
        response = send_message(st.session_state.pending_message, st.session_state.session_id)
        if "error" not in response:
            ai_message = {
                "type": "ai",
                "content": response["response"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            ai_message = {
                "type": "ai",
                "content": f"오류: {response.get('error', '알 수 없는 오류')}",
                "timestamp": datetime.now().isoformat()
            }
        st.session_state.chat_history.append(ai_message)
    st.session_state.is_loading = False
    st.session_state.pending_message = None
    st.rerun()

# 메시지 입력 영역
st.divider()

# 입력 힌트 표시
st.markdown("""
<div class="input-hint">
    💡 메시지를 입력하고 <strong>전송 버튼</strong>을 클릭하세요
</div>
""", unsafe_allow_html=True)

# 메시지 입력 컨테이너
with st.container():
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    # 메시지 입력
    input_key = f"message_input_{st.session_state.clear_input_flag}"
    message_input = st.text_area(
        "메시지를 입력하세요...", 
        height=120, 
        key=input_key,
        help="메시지를 입력하고 전송 버튼을 클릭하세요",
        disabled=st.session_state.is_loading
    )
    
    # 버튼 영역
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        button_text = "⏳ 처리 중..." if st.session_state.is_loading else "📤 전송"
        button_type = "secondary" if st.session_state.is_loading else "primary"
        
        if st.button(button_text, type=button_type, key="send_button", use_container_width=True, disabled=st.session_state.is_loading):
            if not st.session_state.is_loading and message_input.strip():
                user_message = {
                    "type": "human",
                    "content": message_input,
                    "timestamp": datetime.now().isoformat()
                }
                st.session_state.chat_history.append(user_message)
                st.session_state.pending_message = message_input
                st.session_state.is_loading = True
                st.session_state.clear_input_flag = True
                st.rerun()
    
    with col2:
        if st.button("🗑️ 초기화", key="clear_input", use_container_width=True, disabled=st.session_state.is_loading):
            st.session_state.clear_input_flag = not st.session_state.clear_input_flag
            st.rerun()
    
    with col3:
        if st.button("🔄 새로고침", key="refresh_button", use_container_width=True, disabled=st.session_state.is_loading):
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# 푸터
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    멀티 에이전트 채팅 시스템 | Powered by LangChain & Streamlit
</div>
""", unsafe_allow_html=True) 