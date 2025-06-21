from langchain_core.messages import HumanMessage, AIMessage, FunctionMessage
from langchain_core.agents import AgentFinish, AgentActionMessageLog
from app.domain.graph.memory import chat_memory

def agent_node(state, agent, name):
    # 필수 상태 변수들 추가
    if "intermediate_steps" not in state:
        state["intermediate_steps"] = []
    if "agent_scratchpad" not in state:
        state["agent_scratchpad"] = []
    if "session_id" not in state:
        state["session_id"] = None

    result = agent.invoke(state)
    
    # AgentFinish 처리
    if isinstance(result, AgentFinish):
        content = result.return_values.get("output", "")
        response_message = HumanMessage(content=content, name=name)
        
        # 메모리에 응답 저장
        if state.get("session_id"):
            chat_memory.add_message(state["session_id"], response_message)
        
        return {
            "messages": [response_message]
        }
    
    # AgentActionMessageLog 처리 (도구 호출)
    if isinstance(result, AgentActionMessageLog):
        # 도구 실행
        tool_name = result.tool
        tool_input = result.tool_input
        
        # 도구 함수 찾기 및 실행
        tool_func = None
        for tool in agent.tools:
            if tool.name == tool_name:
                tool_func = tool.func
                break
        
        if tool_func:
            try:
                # 도구 실행 - tool_input이 딕셔너리가 아닐 경우 처리
                if isinstance(tool_input, dict):
                    tool_result = tool_func(**tool_input)
                else:
                    tool_result = tool_func(tool_input)
                
                # FunctionMessage 생성
                function_message = FunctionMessage(
                    content=str(tool_result),
                    name=tool_name
                )
                
                # intermediate_steps 업데이트
                new_intermediate_steps = state.get("intermediate_steps", []) + [
                    (result, function_message)
                ]
                
                return {
                    "messages": [function_message],
                    "intermediate_steps": new_intermediate_steps
                }
            except Exception as e:
                error_msg = f"도구 실행 중 오류 발생: {str(e)}"
                error_message = HumanMessage(content=error_msg, name=name)
                
                # 메모리에 오류 메시지 저장
                if state.get("session_id"):
                    chat_memory.add_message(state["session_id"], error_message)
                
                return {
                    "messages": [error_message]
                }
        else:
            error_msg = f"도구를 찾을 수 없습니다: {tool_name}"
            error_message = HumanMessage(content=error_msg, name=name)
            
            # 메모리에 오류 메시지 저장
            if state.get("session_id"):
                chat_memory.add_message(state["session_id"], error_message)
            
            return {
                "messages": [error_message]
            }
    
    # 기타(기존 방식)
    else:
        response_content = result["messages"][-1].content
        response_message = HumanMessage(content=response_content, name=name)
        
        # 메모리에 응답 저장
        if state.get("session_id"):
            chat_memory.add_message(state["session_id"], response_message)
        
        return {
            "messages": [response_message]
        }