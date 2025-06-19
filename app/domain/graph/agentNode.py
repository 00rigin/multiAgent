from langchain_core.messages import HumanMessage
from langchain_core.agents import AgentFinish


def agent_node(state, agent, name):
    if "intermediate_steps" not in state:
        state["intermediate_steps"] = []
    result = agent.invoke(state)
    if isinstance(result, AgentFinish):
        # AgentFinish 객체의 return_values에서 메시지 추출 (output 또는 적절한 key 사용)
        content = result.return_values.get("output", "")
        return {
            "messages": [HumanMessage(content=content, name=name)]
        }
    else:
        return {
            "messages": [HumanMessage(content=result["messages"][-1].content, name=name)]
        }