from langgraph.prebuilt import create_react_agent

from app.config.ai import openai_chat
from app.domain.agents.calenderMaker.KakaoCalenderWrapper import KakaoCalenderWrapper
from langchain_core.tools import Tool


class CalenderAgent:
    def __init__(self, llm = None):
        self.llm = llm or openai_chat
        self.wrapper = KakaoCalenderWrapper()

        self.calender_post_tool = Tool(
            name="kakao_calender",
            func=self._sync_post_event,
            description=(
                "카카오 톡 캘린더에 대한 일정 등록 도구입니다. "
            )
        )

        self.agent = create_react_agent(
            self.llm,
            tools=[self.calender_post_tool],
            prompt="You are a helpful agent that can post events to Kakao Calendar. "
        )

    def _sync_post_event(self, title:str, description: str, strat_at: str, end_at: str) -> bool:
        if self.wrapper.run(title, description, strat_at, end_at) is not None:
            return True
        return False


