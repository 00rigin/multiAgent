from typing import Literal

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel

from app.config.ai import openai_chat

members = ["Researcher", "General"]
system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    "following workers: {members}. Given the following user request,"
    "respond with the worker to act next. Each worker will perform a"
    "task and respond with their results and status. When finished,"
    "respond with FINISH."
)

options = ["FINISH"] + members

class routeResponse(BaseModel):
    next: Literal["FINISH", "Researcher", "General"]

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        (
            "System",
            "Given the conversation above, who should act next? "
            "Respond with one of the following options: {options}. "
            "If the task is complete, respond with FINISH.",
        )
    ]
).partial(options=str(options), members=", ".join(members))

def supervisor_agent(state):
    supervisor_chain = (
        prompt
        | openai_chat.with_structured_output(routeResponse)
    )
    return supervisor_chain.invoke(state)

