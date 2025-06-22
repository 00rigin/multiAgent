"""
그래프 레벨 가드레일 노드

사용자 입력과 AI 응답을 검사하는 가드레일 시스템
"""

from typing import Dict, Any
from app.domain.gaurdrails.guardrails import guardrail_system


def input_guardrail_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    사용자 입력을 검사하는 가드레일 노드
    
    Args:
        state: 현재 상태
        
    Returns:
        검사 결과를 포함한 상태
    """
    messages = state.get("messages", [])
    
    # 사용자의 마지막 메시지 찾기
    user_messages = [msg for msg in messages if hasattr(msg, 'type') and msg.type == "human"]
    
    if not user_messages:
        # 사용자 메시지가 없으면 그대로 통과
        return state
    
    # 가장 최근 사용자 메시지 검사
    latest_user_message = user_messages[-1].content
    
    # 가드레일 검사
    safety_result = guardrail_system.check_input_safety(latest_user_message)
    
    if not safety_result.is_safe:
        # 안전하지 않은 요청에 대한 응답 생성
        response = guardrail_system.get_safe_response(safety_result.reason)
        
        # 추가 안내 메시지
        if safety_result.suggestions:
            response += f"\n\n💡 제안: {', '.join(safety_result.suggestions)}"
        
        # 가드레일 차단 정보를 상태에 추가
        state["guardrail_blocked"] = True
        state["guardrail_response"] = response
        state["guardrail_reason"] = safety_result.reason
        
        print(f"🛡️ Input Guardrail blocked: {safety_result.reason}")
        print(f"Blocked keywords: {safety_result.blocked_keywords}")
    
    return state


def output_guardrail_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    AI 응답을 검사하는 가드레일 노드
    
    Args:
        state: 현재 상태
        
    Returns:
        검사 결과를 포함한 상태
    """
    messages = state.get("messages", [])
    
    # AI의 마지막 응답 찾기
    ai_messages = [msg for msg in messages if hasattr(msg, 'type') and msg.type == "ai"]
    
    if not ai_messages:
        # AI 응답이 없으면 그대로 통과
        return state
    
    # 가장 최근 AI 응답 검사
    latest_ai_message = ai_messages[-1].content
    
    # 가드레일 검사
    safety_result = guardrail_system.check_input_safety(latest_ai_message)
    
    if not safety_result.is_safe:
        # 안전하지 않은 응답에 대한 대체 메시지 생성
        response = "죄송합니다. 안전하지 않은 내용이 포함된 응답이 생성되었습니다. 다시 시도해주세요."
        
        # 가드레일 차단 정보를 상태에 추가
        state["output_guardrail_blocked"] = True
        state["output_guardrail_response"] = response
        state["output_guardrail_reason"] = safety_result.reason
        
        print(f"🛡️ Output Guardrail blocked: {safety_result.reason}")
        print(f"Blocked keywords: {safety_result.blocked_keywords}")
    
    return state


def check_guardrail_blocked(state: Dict[str, Any]) -> str:
    """
    가드레일이 차단되었는지 확인하고 다음 노드를 결정
    
    Args:
        state: 현재 상태
        
    Returns:
        다음 노드 이름
    """
    # 입력 가드레일이 차단된 경우
    if state.get("guardrail_blocked", False):
        return "guardrail_response"
    
    # 출력 가드레일이 차단된 경우
    if state.get("output_guardrail_blocked", False):
        return "output_guardrail_response"
    
    # 정상적인 경우 supervisor로 진행
    return "supervisor"


def guardrail_response_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    가드레일 차단 시 응답을 생성하는 노드
    
    Args:
        state: 현재 상태
        
    Returns:
        가드레일 응답을 포함한 상태
    """
    from langchain_core.messages import AIMessage
    
    response = state.get("guardrail_response", "죄송합니다. 안전상의 이유로 해당 요청을 처리할 수 없습니다.")
    
    # AI 메시지로 응답 생성
    ai_message = AIMessage(content=response)
    
    # 메시지 리스트에 추가
    messages = state.get("messages", [])
    messages.append(ai_message)
    
    return {
        "messages": messages,
        "next": "FINISH"  # 가드레일 차단 시 바로 종료
    }


def output_guardrail_response_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    출력 가드레일 차단 시 응답을 생성하는 노드
    
    Args:
        state: 현재 상태
        
    Returns:
        가드레일 응답을 포함한 상태
    """
    from langchain_core.messages import AIMessage
    
    response = state.get("output_guardrail_response", "죄송합니다. 안전하지 않은 응답이 생성되었습니다.")
    
    # AI 메시지로 응답 생성
    ai_message = AIMessage(content=response)
    
    # 메시지 리스트에 추가
    messages = state.get("messages", [])
    messages.append(ai_message)
    
    return {
        "messages": messages,
        "next": "FINISH"  # 가드레일 차단 시 바로 종료
    } 