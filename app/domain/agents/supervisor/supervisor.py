from typing import Literal

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel

from app.config.ai import openai_chat
from app.config.prompts import get_prompt


class routeResponse(BaseModel):
    next: Literal["FINISH", "Researcher", "Calender", "Chat", "Mail"]


class Supervisor:
    def __init__(self, llm=None):
        self.llm = llm or openai_chat

        self.members = ["Researcher", "Calender", "Chat", "Mail"]
        
        # 프롬프트 가져오기
        system_prompt = get_prompt('supervisor').format(
            members=", ".join(self.members),
            options=str(["FINISH"] + self.members)
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        self.chain = (
                prompt
                | self.llm.with_structured_output(routeResponse)
        )

    def invoke(self, state):
        return self.chain.invoke(state)
