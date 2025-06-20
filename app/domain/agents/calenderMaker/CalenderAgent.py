from langgraph.prebuilt import create_react_agent
from langchain.agents import create_openai_functions_agent
from app.config.ai import openai_chat
from app.domain.agents.calenderMaker.KakaoCalenderWrapper import KakaoCalenderWrapper
from app.domain.agents.calenderMaker.CalenderParams import CalenderParams
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.agents import AgentFinish
from langchain_core.messages import HumanMessage, AIMessage, FunctionMessage
from langchain_core.agents import AgentActionMessageLog
from langchain_core.tools import tool
import json

class CalenderAgent:
    def __init__(self, llm = None):
        self.llm = llm or openai_chat
        self.wrapper = KakaoCalenderWrapper()

        # self.calender_post_tool = Tool(
        #     name="kakao_calender",
        #     func=self._sync_post_event,
        #     description=(
        #         "카카오 캘린더에 일정을 등록하는 도구입니다. "
        #         "필요한 정보(제목, 설명, 시작 시간, 종료 시간)가 모두 주어졌을 때만 사용하세요. "
        #         "예시: {'title': '여행', 'description': '불국사 방문', 'start_at': '2024-06-01 10:00', 'end_at': '2024-06-01 11:00'}"
        #     ),
        #     returns=bool
        # )

        
        @tool(
            args_schema=CalenderParams,
        )
        def kakao_calendar(args: CalenderParams) -> bool:
            """
            카카오 캘린더에 일정을 등록하는 도구입니다.
            예시: {'title': '여행', 'description': '불국사 방문', 'start_at': '2024-06-01 10:00', 'end_at': '2024-06-01 11:00'}
            """
            return self.wrapper.run(
                args.title, args.description, args.start_at, args.end_at
            ) is not None

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
            tools=[kakao_calendar],
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

        # 도구를 인스턴스 변수로 저장 (루프에서 사용)
        self.kakao_calendar = kakao_calendar

    # def post_event(self, params: CalenderParams) -> bool:
    #     return self._sync_post_event(params.title, params.description, params.start_at, params.end_at)

    # def _sync_post_event(self, title:str, description: str, start_at: str, end_at: str) -> bool:
    #     if self.wrapper.run(title, description, start_at, end_at) is not None:
    #         return True
    #     return False

    # 4. 메시지 루프 (핵심)
    def run(self, user_input: str):
        messages = [HumanMessage(content=user_input)]
        while True:
            response = self.agent.invoke({"messages": messages})
            # 4-1. 최종 답변이면 반환
            if isinstance(response, AgentFinish):
                return response.return_values.get("output", "")
            # 4-2. function_call이면 도구 실행 → FunctionMessage로 결과 전달
            elif isinstance(response, AIMessage):
                func_call = response.additional_kwargs.get("function_call")
                if func_call:
                    func_name = func_call.get("name")
                    args = func_call.get("arguments")
                    args_dict = json.loads(args) if args else {}
                    # 실제 도구 실행
                    result = self.kakao_calendar(args_dict)
                    # 메시지 버퍼에 function_call, FunctionMessage 추가
                    messages.append(response)
                    messages.append(FunctionMessage(
                        name=func_name,
                        content=json.dumps(result)
                    ))
                else:
                    # 일반 assistant 메시지면 그냥 추가
                    messages.append(response)
            else:
                # 기타 메시지면 그냥 추가
                messages.append(response)


