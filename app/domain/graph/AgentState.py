import operator
from typing import Annotated, TypedDict, Sequence, Optional, List, Tuple

from langchain_core.messages import BaseMessage
from langchain_core.agents import AgentActionMessageLog

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    session_id: Optional[str]
    agent_scratchpad: Annotated[Sequence[BaseMessage], operator.add]
    intermediate_steps: List[Tuple[AgentActionMessageLog, BaseMessage]]