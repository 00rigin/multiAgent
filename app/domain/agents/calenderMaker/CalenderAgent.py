from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
from typing import Optional

from app.config.ai import openai_chat
from app.component.calendar.KakaoCalendar.KaKaoCalendarComponent import KakaoCalendarComponent
from app.component.calendar.CalendarInterface import CalendarInterface


class CalenderAgent:
    def __init__(self, llm=None, calendar_component: Optional[CalendarInterface] = None):
        """
        Initialize CalenderAgent with optional calendar component.
        
        Args:
            llm: Language model to use
            calendar_component: Calendar implementation (defaults to KakaoCalendarComponent)
        """
        self.llm = llm or openai_chat
        
        # Calendar component initialization
        if calendar_component:
            self.calendar = calendar_component
        else:
            # Default to Kakao Calendar
            self.calendar = KakaoCalendarComponent()

        def create_calendar_event_tool(title: str, description: str, start_at: str, end_at: str, all_day: bool = False) -> str:
            """
            Create a new calendar event.
            
            Args:
                title: 일정 제목
                description: 일정 설명
                start_at: 일정 시작 시간 (ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ)
                end_at: 일정 종료 시간 (ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ)
                all_day: 종일 일정 여부 (기본값: False)
            """
            print("============ Create Calendar Event ===============")
            print(f"Title: {title}")
            print(f"Description: {description}")
            print(f"Start: {start_at}")
            print(f"End: {end_at}")
            print(f"All Day: {all_day}")
            
            try:
                result = self.calendar.create_event(
                    title=title,
                    description=description,
                    start_at=start_at,
                    end_at=end_at,
                    all_day=all_day,
                    lunar=False
                )
                
                print(f"Calendar API Response: {result}")
                
                if result and "event_id" in result:
                    return f"일정 생성 성공: {title} ({start_at} ~ {end_at}) - 이벤트 ID: {result['event_id']}"
                else:
                    return f"일정 생성 성공: {title} ({start_at} ~ {end_at})"
                    
            except Exception as e:
                error_msg = f"일정 생성에 실패했습니다: {str(e)}"
                print(f"Error: {error_msg}")
                return error_msg

        def get_details_event_tool(event_id: str) -> str:
            """
            Get details of a calendar event.

            Args:
                event_id: 일정의 ID
            """
            print("============ Get Calendar Event Details ===============")
            print(f"Event ID: {event_id}")

            try:
                result = self.calendar.get_events(event_id=event_id)

                print(f"Calendar API Response: {result}")

                if result and "event" in result:
                    event = result["event"]
                    return f"일정 상세 정보: {event}"
                else:
                    return "일정 정보를 찾을 수 없습니다."

            except Exception as e:
                error_msg = f"일정 정보를 가져오는 데 실패했습니다: {str(e)}"
                print(f"Error: {error_msg}")
                return error_msg

        def update_calendar_event_tool(event_id: str, title: Optional[str] = None, 
                                     description: Optional[str] = None, start_at: Optional[str] = None,
                                     end_at: Optional[str] = None) -> str:
            """
            Update an existing calendar event.
            
            Args:
                event_id: 수정할 일정의 ID
                title: 새로운 제목 (선택사항)
                description: 새로운 설명 (선택사항)
                start_at: 새로운 시작 시간 (선택사항)
                end_at: 새로운 종료 시간 (선택사항)
            """
            print("============ Update Calendar Event ===============")
            print(f"Event ID: {event_id}")
            print(f"New Title: {title}")
            print(f"New Description: {description}")
            print(f"New Start: {start_at}")
            print(f"New End: {end_at}")
            
            try:
                result = self.calendar.update_event(
                    event_id=event_id,
                    title=title,
                    description=description,
                    start_at=start_at,
                    end_at=end_at
                )
                
                print(f"Calendar API Response: {result}")
                
                if result:
                    return f"일정 수정 성공: 이벤트 ID {event_id}"
                else:
                    return "일정 수정에 실패했습니다."
                    
            except Exception as e:
                error_msg = f"일정 수정에 실패했습니다: {str(e)}"
                print(f"Error: {error_msg}")
                return error_msg

        def delete_calendar_event_tool(event_id: str) -> str:
            """
            Delete a calendar event.
            
            Args:
                event_id: 삭제할 일정의 ID
            """
            print("============ Delete Calendar Event ===============")
            print(f"Event ID: {event_id}")
            
            try:
                result = self.calendar.delete_event(event_id=event_id)
                
                print(f"Calendar API Response: {result}")
                
                if result:
                    return f"일정 삭제 성공: 이벤트 ID {event_id}"
                else:
                    return "일정 삭제에 실패했습니다."
                    
            except Exception as e:
                error_msg = f"일정 삭제에 실패했습니다: {str(e)}"
                print(f"Error: {error_msg}")
                return error_msg

        # 도구들 생성
        self.create_event_tool = tool(create_calendar_event_tool)
        self.get_details_event_tool = tool(get_details_event_tool)
        self.update_event_tool = tool(update_calendar_event_tool)
        self.delete_event_tool = tool(delete_calendar_event_tool)

        # React Agent 생성
        self.agent = create_react_agent(
            self.llm,
            tools=[
                self.create_event_tool,
                self.get_details_event_tool,
                self.update_event_tool,
                self.delete_event_tool,
            ],
            prompt="""너는 사용자의 요청을 받아 캘린더를 완전히 관리하는 에이전트야.

주요 기능:
1. 일정 생성: 새로운 일정을 캘린더에 등록
2. 일정 조회: 특정 일정의 상세 정보를 가져옴
3. 일정 수정: 기존 일정의 정보를 수정
4. 일정 삭제: 기존 일정을 삭제

사용 가능한 도구들:
- create_calendar_event_tool: 일정 생성
- get_details_event_tool: 일정 상세 조회
- update_calendar_event_tool: 일정 수정
- delete_calendar_event_tool: 일정 삭제

일정 시간 형식: ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)
예시:
- "내일 오후 2시부터 4시까지 회의" : 오늘이 2025.06.22 라면 → start_at: "2025-06-23T14:00:00Z", end_at: "2025-06-23T16:00:00Z"
- "다음주 월요일 종일 휴가":  오늘이 2025.06.22 라면 → start_at: "2025-06-30T00:00:00Z", end_at: "2025-06-30T23:59:59Z", all_day: True

사용자의 요청을 분석하여 적절한 도구를 선택하고 실행해줘.
도구 사용에 성공 했을때, 도구 사용 결과와 key를 반환해줘.
"""
        )
    
    def run(self, message: str) -> str:
        """
        Run the calendar agent with a user message.
        
        Args:
            message: User's message requesting calendar operations
            
        Returns:
            Agent's response
        """
        try:
            # Agent 실행
            result = self.agent.invoke({"input": message})
            return result["output"]
        except Exception as e:
            error_msg = f"에이전트 실행 중 오류가 발생했습니다: {str(e)}"
            print(f"Agent Error: {error_msg}")
            return error_msg