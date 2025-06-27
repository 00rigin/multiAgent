import functools
from typing import Hashable

from langgraph.graph import StateGraph, END, START

from app.domain.agents.calenderMaker.CalenderAgent import CalenderAgent
from app.domain.agents.researcher.SearchAgent import SearchAgent
from app.domain.agents.advisor.ChatAgent import ChatAgent
from app.domain.agents.supervisor.supervisor import Supervisor
from app.domain.agents.mailAgent.MailAgent import MailAgent
from app.domain.graph.AgentState import AgentState
from app.domain.graph.agentNode import agent_node
from app.domain.gaurdrails.guardrailNode import (
    input_guardrail_node,
    output_guardrail_node,
    check_guardrail_blocked,
    guardrail_response_node,
    output_guardrail_response_node
)


class GraphSetup:

    def __init__(self):
        self.search_agent = SearchAgent()
        self.calender_agent = CalenderAgent()
        self.chat_agent = ChatAgent()
        self.mail_agent = MailAgent()
        self.supervisor = Supervisor()

    def setup_graph(self):
        workflow = StateGraph(AgentState)

        # 가드레일 노드들 추가
        workflow.add_node("input_guardrail", input_guardrail_node)
        # workflow.add_node("output_guardrail", output_guardrail_node)
        workflow.add_node("guardrail_response", guardrail_response_node)
        # workflow.add_node("output_guardrail_response", output_guardrail_response_node)

        # 기존 에이전트 노드들
        search_node = functools.partial(
            agent_node,
            agent=self.search_agent.agent,
            name="Researcher",
        )
        calender_node = functools.partial(
            agent_node,
            agent=self.calender_agent.agent,
            name="Calender",
        )
        mail_node = functools.partial(
            agent_node,
            agent=self.mail_agent.agent,
            name="Mail",
        )

        workflow.add_node("Researcher", search_node)
        workflow.add_node("Calender", calender_node)
        workflow.add_node("Mail", mail_node)
        workflow.add_node("Chat", self.chat_agent.invoke)
        workflow.add_node("supervisor", self.supervisor.invoke)

        # 에이전트에서 supervisor로의 엣지
        workflow.add_edge("Researcher", "supervisor")
        workflow.add_edge("Calender", "supervisor")
        workflow.add_edge("Mail", "supervisor")
        workflow.add_edge("Chat", "supervisor")
        # workflow.add_edge("Researcher", "output_guardrail")
        # workflow.add_edge("Calender", "output_guardrail")
        # workflow.add_edge("Mail", "output_guardrail")
        # workflow.add_edge("Chat", "output_guardrail")

        # # 출력 가드레일에서 supervisor로의 조건부 엣지
        # workflow.add_conditional_edges(
        #     "output_guardrail",
        #     check_guardrail_blocked,
        #     {
        #         "supervisor": "supervisor",
        #         "output_guardrail_response": "output_guardrail_response"
        #     }
        # )

        # supervisor에서 각 에이전트로의 조건부 엣지
        conditional_map: dict[Hashable, str] = {
            "Researcher": "Researcher", 
            "Calender": "Calender", 
            "Mail": "Mail",
            "Chat": "Chat",
            "FINISH": END
        }
        workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)

        workflow.add_edge(START, "supervisor")

        # 시작점 설정: 입력 가드레일 -> 조건부 분기
        # workflow.add_edge(START, "input_guardrail")
        # workflow.add_conditional_edges(
        #     "input_guardrail",
        #     check_guardrail_blocked,
        #     {
        #         "supervisor": "supervisor",
        #         "guardrail_response": "guardrail_response"
        #     }
        # )
        #
        # # 가드레일 응답 노드에서 종료
        # workflow.add_edge("guardrail_response", END)
        # workflow.add_edge("output_guardrail_response", END)

        return workflow.compile()



