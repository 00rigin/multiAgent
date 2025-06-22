from typing import Literal

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel

from app.config.ai import openai_chat


class routeResponse(BaseModel):
    next: Literal["FINISH", "Researcher", "Calender", "Chat", "Mail"]


class Supervisor:
    def __init__(self, llm=None):
        self.llm = llm or openai_chat

        self.members = ["Researcher", "Calender", "Chat", "Mail"]
        system_prompt = (
            "You are a supervisor tasked with managing a conversation between the"
            " following workers: {members}. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH.\n\n"
            "- Researcher: 검색이나 정보 조사가 필요한 경우\n"
            "- Calender: 일정 관리나 캘린더 등록이 필요한 경우\n"
            "- Chat: 일반적인 대화나 질문에 답변이 필요한 경우"
            "- Mail: 외부 공유 , 이메일 발송이 필요한 경우\n\n"
        )

        options = ["FINISH"] + self.members

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Given the conversation above, who should act next? "
                    "Respond with one of the following options: {options}. "
                    "If the task is complete, respond with FINISH.",
                )
            ]
        ).partial(options=str(options), members=", ".join(self.members))

        self.chain = (
                prompt
                | self.llm.with_structured_output(routeResponse)
        )

    def invoke(self, state):
        return self.chain.invoke(state)
