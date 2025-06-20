from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.agents import AgentFinish, AgentActionMessageLog

def agent_node(state, agent, name):
    if "intermediate_steps" not in state:
        state["intermediate_steps"] = []
    result = agent.invoke(state)
    # AgentFinish 처리
    if isinstance(result, AgentFinish):
        content = result.return_values.get("output", "")
        return {
            "messages": [HumanMessage(content=content, name=name)]
        }
    # AgentActionMessageLog 처리
    if isinstance(result, AgentActionMessageLog):
        # message_log의 마지막 메시지가 AIMessage(function_call)일 수 있음
        last_msg = result.message_log[-1] if result.message_log else None
        if isinstance(last_msg, AIMessage) and hasattr(last_msg, "additional_kwargs"):
            func_call = last_msg.additional_kwargs.get("function_call")
            if func_call:
                func_name = func_call.get("name")
                args = func_call.get("arguments")
                # arguments는 JSON string일 수 있으니 파싱
                import json
                try:
                    args_dict = json.loads(args) if args else {}
                except Exception:
                    args_dict = {}
                # 안내 메시지 생성
                content = f"{func_name} 도구를 호출합니다. 입력값: {args_dict}"
            else:
                content = ""
        else:
            content = last_msg.content if last_msg else ""
        return {
            "messages": [HumanMessage(content=content, name=name)]
        }
    # 기타(기존 방식)
    else:
        return {
            "messages": [HumanMessage(content=result["messages"][-1].content, name=name)]
        }