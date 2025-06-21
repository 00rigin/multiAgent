from langgraph.prebuilt import create_react_agent
from langchain.tools import tool

from app.config.ai import openai_chat
from app.domain.agents.calenderMaker.KakaoCalenderWrapper import KakaoCalenderWrapper


class CalenderAgent:
    def __init__(self, llm = None):
        self.llm = llm or openai_chat
        self.wrapper = KakaoCalenderWrapper()

        # 도구 함수를 별도로 정의
        def kakao_calendar_tool(title: str, description: str, start_at: str, end_at: str) -> str:
            """
            This is a tool to register your schedule in your Kakao calendar.
            title: 일정 제목
            description: 일정 설명
            start_at: 일정 시작 시간()
            end_at: 일정 종료 시간
            """
            print("============kakao_calender===============")
            result = self.wrapper.run(
                title, description, start_at, end_at
            )
            if result:
                return f"일정 등록 성공: {title} ({start_at} ~ {end_at})"
            else:
                return "일정 등록에 실패했습니다."

        # 도구 생성
        self.kakao_calendar_tool = tool(kakao_calendar_tool)

        # React Agent 생성 (AgentExecutor 없이)
        self.agent = create_react_agent(
            self.llm,
            tools=[self.kakao_calendar_tool],
            prompt="너는 사용자의 요청을 받아 카카오 캘린더에 일정을 등록하는 에이전트야. kakao_calendar 도구를 사용해서 일정을 등록해줘."
        )