import functools
from typing import Hashable

from langgraph.graph import StateGraph, END, START
from mypy.types import names

from app.domain.agents.calenderMaker.CalenderAgent import CalenderAgent
from app.domain.agents.researcher.SearchAgent import SearchAgent
from app.domain.agents.advisor.chat_agent import ChatAgent
from app.domain.agents.supervisor.supervisor import supervisor_agent
from app.domain.agents.mailAgent.MailAgent import MailAgent
from app.domain.graph.AgentState import AgentState
from app.domain.graph.agentNode import agent_node


class GraphSetup:

    def __init__(self):
        self.search_agent = SearchAgent()
        self.calender_agent = CalenderAgent()
        self.chat_agent = ChatAgent()
        self.mail_agent = MailAgent()

    def setup_graph(self):
        workflow = StateGraph(AgentState)

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
        workflow.add_node("supervisor", supervisor_agent)

        workflow.add_edge("Researcher", "supervisor")
        workflow.add_edge("Calender", "supervisor")
        workflow.add_edge("Mail", "supervisor")
        workflow.add_edge("Chat", "supervisor")

        conditional_map: dict[Hashable, str] = {
            "Researcher": "Researcher", 
            "Calender": "Calender", 
            "Mail": "Mail",
            "Chat": "Chat",
            "FINISH": END
        }
        workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)

        workflow.add_edge(START, "supervisor")

        return workflow.compile()



