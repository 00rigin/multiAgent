from langgraph.prebuilt import create_react_agent
from langchain.agents import create_openai_functions_agent
from app.config.ai import openai_chat
from app.domain.agents.calenderMaker.KakaoCalenderWrapper import KakaoCalenderWrapper
from app.domain.agents.calenderMaker.CalenderParams import CalenderParams
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.agents import AgentFinish
from langchain_core.messages import HumanMessage, AIMessage, FunctionMessage, BaseMessage
from langchain_core.agents import AgentActionMessageLog
from langchain_core.tools import tool
import json

class CalenderAgent:
    def __init__(self, llm = None):
        self.llm = llm or openai_chat
        self.wrapper = KakaoCalenderWrapper()

        self.calender_post_tool = Tool(
            name="kakao_calender",
            func=self._sync_post_event,
            description=(
                "카카오 캘린더에 일정을 등록하는 도구입니다. "
                "입력(title: str, description: str, start_at: str, end_at: str) → 일정 등록 결과(bool) 반환"
            ),
        )


        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", 
                 "너는 사용자의 요청을 받아 카카오 캘린더에 일정을 등록하는 에이전트야. "
                 "사용자가 모든 정보를 주지 않아도, 대화 맥락이나 일반 상식에 따라 적당한 title, description, start_at, end_at 값을 추론해서 반드시 일정을 등록해야 해."),
                ("user", "내일 오전에 친구랑 점심 약속 잡아줘"),
                AIMessage(
                    content="",
                    additional_kwargs={
                        "function_call": {
                            "name": "kakao_calendar",
                            "arguments": '{"title": "친구와 점심", "description": "친구와 점심 약속", "start_at": "2024-06-02T11:00:00", "end_at": "2024-06-02T12:00:00"}'
                        }
                    }
                ),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
                ("system", "아래 도구를 사용할 수 있어:\n"
                           "kakao_calendar: 카카오 캘린더에 일정을 등록하는 도구"),
            ]
        )

        self.agent = create_openai_functions_agent(
            self.llm,
            tools=[self.calender_post_tool],
            prompt=prompt
        )


    def _sync_post_event(self, arg1: str) -> bool:
        # arg1이 JSON 문자열이므로 파싱
        params = json.loads(arg1)
        title = params["title"]
        description = params["description"]
        start_at = params["start_at"]
        end_at = params["end_at"]
        print("============run post calender===============")
        print(title, description, start_at, end_at)
        return self.wrapper.run(title, description, start_at, end_at) is not None



