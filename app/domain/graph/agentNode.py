from langchain_core.messages import HumanMessage, AIMessage, FunctionMessage
from langchain_core.agents import AgentFinish, AgentActionMessageLog
from app.domain.graph.memory import chat_memory


def initialize_state(state):
    if "agent_scratchpad" not in state:
        state["agent_scratchpad"] = []
    if "session_id" not in state:
        state["session_id"] = None
    return state


def save_to_memory(message, session_id):
    if session_id:
        chat_memory.add_message(session_id, message)


def execute_tool(tool_name, tool_input, agent):
    tool_func = None
    for tool in agent.tools:
        if tool.name == tool_name:
            tool_func = tool.func
            break
    
    if not tool_func:
        raise ValueError(f"도구를 찾을 수 없습니다: {tool_name}")
    
    if isinstance(tool_input, dict):
        return tool_func(**tool_input)
    else:
        return tool_func(tool_input)


def handle_agent_finish(result, name, session_id):
    content = result.return_values.get("output", "")
    response_message = AIMessage(content=content, name=name)
    
    save_to_memory(response_message, session_id)
    return {"messages": [response_message]}


def handle_agent_action(result, agent, name, state):
    try:
        tool_result = execute_tool(result.tool, result.tool_input, agent)
        
        function_message = FunctionMessage(
            content=str(tool_result),
            name=result.tool
        )
        
        new_intermediate_steps = state.get("intermediate_steps", []) + [
            (result, function_message)
        ]
        
        return {
            "messages": [function_message],
            "intermediate_steps": new_intermediate_steps
        }
        
    except Exception as e:
        error_msg = f"도구 실행 중 오류 발생: {str(e)}"
        error_message = AIMessage(content=error_msg, name=name)
        
        save_to_memory(error_message, state.get("session_id"))
        return {"messages": [error_message]}


def handle_regular_response(result, name, session_id):
    response_content = result["messages"][-1].content
    response_message = AIMessage(content=response_content, name=name)
    
    save_to_memory(response_message, session_id)
    return {"messages": [response_message]}


def agent_node(state, agent, name):
    state = initialize_state(state)
    
    result = agent.invoke(state)
    
    if isinstance(result, AgentFinish):
        return handle_agent_finish(result, name, state.get("session_id"))
    
    elif isinstance(result, AgentActionMessageLog):
        return handle_agent_action(result, agent, name, state)
    
    else:
        return handle_regular_response(result, name, state.get("session_id"))