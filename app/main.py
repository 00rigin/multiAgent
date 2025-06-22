import uuid
from datetime import datetime

from fastapi import FastAPI
from langchain_core.messages import HumanMessage

from app.MessageRequest import MessageRequest
from app.domain.graph.TravelChatGraph import TravelChatGraph
from app.domain.graph.memory import chat_memory

app = FastAPI(debug=True)
travel_chatbot = TravelChatGraph()

@app.get("/health")
async def health_check():
    """서버 상태를 확인하는 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Multi-Agent Chat API"
    }

@app.post("/chat")
async def test(request: MessageRequest):
    # 세션 ID 생성 또는 기존 세션 사용
    session_id = request.session_id or str(uuid.uuid4())
    
    # 기존 메시지 히스토리 가져오기
    existing_messages = chat_memory.get_messages(session_id)
    
    # 새로운 사용자 메시지 추가
    user_message = HumanMessage(content=request.message)
    chat_memory.add_message(session_id, user_message)
    
    # 현재 세션의 모든 메시지로 상태 초기화
    current_messages = existing_messages + [user_message]
    
    messages = []
    final_response = None
    
    for s in travel_chatbot.start().stream(
        {
            "messages": current_messages,
            "agent_scratchpad": [],
            "session_id": session_id
        }
    ):
        # 각 노드의 메시지 수집
        for key, value in s.items():
            if key != "__end__" and isinstance(value, dict) and "messages" in value:
                messages.extend(value["messages"])
        
        # 최종 결과 확인
        if "__end__" in s:
            final_response = s["__end__"]
            break
        elif "supervisor" in s and s["supervisor"].get("next") == "FINISH":
            # supervisor가 FINISH를 반환한 경우, 수집된 메시지에서 응답 추출
            if messages:
                # 마지막 메시지의 내용을 반환
                final_response = messages[-1].content
            else:
                final_response = "대화가 완료되었습니다."
            break
    
    if final_response:
        # AI 응답을 메모리에 저장
        from langchain_core.messages import AIMessage
        ai_message = AIMessage(content=final_response)
        chat_memory.add_message(session_id, ai_message)
        
        return {
            "response": final_response,
            "session_id": session_id
        }
    else:
        return {"response": "처리 중 오류가 발생했습니다.", "session_id": session_id}

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """특정 세션의 채팅 히스토리를 반환합니다."""
    messages = chat_memory.get_messages(session_id)
    return {
        "session_id": session_id,
        "messages": [
            {
                "type": "human" if isinstance(msg, HumanMessage) else "ai",
                "content": msg.content
            }
            for msg in messages
        ]
    }

@app.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """특정 세션의 채팅 히스토리를 삭제합니다."""
    chat_memory.clear_session(session_id)
    return {"message": f"세션 {session_id}의 히스토리가 삭제되었습니다."}

@app.get("/chat/stats")
async def get_chat_stats():
    """채팅 통계를 반환합니다."""
    return {
        "active_sessions": chat_memory.get_session_count(),
        "total_messages": chat_memory.get_total_messages()
    }

    