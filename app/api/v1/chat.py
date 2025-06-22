"""
채팅 API 라우터

채팅 관련 엔드포인트를 관리합니다.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage, AIMessage

from app.MessageRequest import MessageRequest
from app.domain.graph.TravelChatGraph import TravelChatGraph
from app.domain.graph.memory import chat_memory

router = APIRouter(prefix="/chat", tags=["chat"])

# 전역 인스턴스
travel_chatbot = TravelChatGraph()


@router.post("/")
async def chat(request: MessageRequest) -> Dict[str, Any]:
    """
    채팅 메시지를 처리하고 응답을 반환합니다.
    
    Args:
        request: 채팅 요청
        
    Returns:
        채팅 응답과 세션 ID
    """
    try:
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
        
        # 그래프 실행
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
            ai_message = AIMessage(content=final_response)
            chat_memory.add_message(session_id, ai_message)
            
            return {
                "response": final_response,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="처리 중 오류가 발생했습니다.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채팅 처리 중 오류: {str(e)}")


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str) -> Dict[str, Any]:
    """
    특정 세션의 채팅 히스토리를 반환합니다.
    
    Args:
        session_id: 세션 ID
        
    Returns:
        세션의 메시지 히스토리
    """
    try:
        messages = chat_memory.get_messages(session_id)
        return {
            "session_id": session_id,
            "messages": [
                {
                    "type": "human" if isinstance(msg, HumanMessage) else "ai",
                    "content": msg.content,
                    "timestamp": datetime.now().isoformat()  # 실제로는 메시지별 타임스탬프 필요
                }
                for msg in messages
            ],
            "message_count": len(messages)
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"세션을 찾을 수 없습니다: {str(e)}")


@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str) -> Dict[str, str]:
    """
    특정 세션의 채팅 히스토리를 삭제합니다.
    
    Args:
        session_id: 세션 ID
        
    Returns:
        삭제 완료 메시지
    """
    try:
        chat_memory.clear_session(session_id)
        return {"message": f"세션 {session_id}의 히스토리가 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 삭제 중 오류: {str(e)}")


@router.get("/stats")
async def get_chat_stats() -> Dict[str, Any]:
    """
    채팅 통계를 반환합니다.
    
    Returns:
        채팅 통계 정보
    """
    try:
        return {
            "active_sessions": chat_memory.get_session_count(),
            "total_messages": chat_memory.get_total_messages(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 중 오류: {str(e)}")


@router.get("/sessions")
async def get_active_sessions() -> Dict[str, Any]:
    """
    활성 세션 목록을 반환합니다.
    
    Returns:
        활성 세션 정보
    """
    try:
        # 실제로는 세션 목록을 반환하는 메서드가 필요
        return {
            "active_sessions": chat_memory.get_session_count(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 목록 조회 중 오류: {str(e)}") 