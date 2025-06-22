import operator
from typing import Annotated, TypedDict, Sequence, Optional

from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    session_id: Optional[str]
    agent_scratchpad: Annotated[Sequence[BaseMessage], operator.add]