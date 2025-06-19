from langgraph.prebuilt import create_react_agent
from langchain.agents import create_openai_functions_agent
from app.config.ai import openai_chat
from app.domain.agents.calenderMaker.KakaoCalenderWrapper import KakaoCalenderWrapper
from app.domain.agents.calenderMaker.CalenderParams import CalenderParams
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder

class CalenderAgent:
    def __init__(self, llm = None):
        self.llm = llm or openai_chat
        self.wrapper = KakaoCalenderWrapper()

        self.calender_post_tool = Tool(
            name="kakao_calender",
            func=self.post_event,
            description=(
                "카카오 톡 캘린더에 대한 일정 등록 도구입니다. "
            ),
            returns=bool
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful agent that can post events to Kakao Calendar. "),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
                ("system", "You can use the following tools to post events to Kakao Calendar: "),
                ("system", "kakao_calender: A tool to post events to Kakao Calendar. ")

            ]
        )

        self.agent = create_openai_functions_agent(
            self.llm,
            tools=[self.calender_post_tool],
            prompt=prompt
        )

        # self.agent = create_react_agent(
        #     self.llm,
        #     tools=[self.calender_post_tool],
        #     prompt="You are a helpful agent that can post events to Kakao Calendar. "
        #     "You can use the following tools to post events to Kakao Calendar: "
        #     "kakao_calender: A tool to post events to Kakao Calendar. "
        #     ""
        # )

    def post_event(self, params: CalenderParams) -> bool:
        return self._sync_post_event(params.title, params.description, params.start_at, params.end_at)

    def _sync_post_event(self, title:str, description: str, strat_at: str, end_at: str) -> bool:
        if self.wrapper.run(title, description, strat_at, end_at) is not None:
            return True
        return False


