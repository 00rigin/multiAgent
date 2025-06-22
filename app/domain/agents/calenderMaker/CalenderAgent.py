from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
from typing import Optional
from datetime import datetime

from app.config.ai import openai_chat
from app.component.calendar.kakaoCalendar.KaKaoCalendarComponent import KakaoCalendarComponent
from app.component.calendar.CalendarInterface import CalendarInterface
from app.config.prompts import get_prompt


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

        def create_calendar_event_tool(title: str, description: str, start_at: str, end_at: str) -> str:
            """
            Create a new calendar event.
            
            Args:
                title: 일정 제목
                description: 일정 설명
                start_at: 일정 시작 시간 (ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ)
                end_at: 일정 종료 시간 (ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ)
            """
            print("============ Create Calendar Event ===============")
            print(f"Title: {title}")
            print(f"Description: {description}")
            print(f"Start: {start_at}")
            print(f"End: {end_at}")
            
            try:
                result = self.calendar.create_event(
                    title=title,
                    description=description,
                    start_at=start_at,
                    end_at=end_at
                )
                
                print(f"Calendar API Response: {result}")
                
                if result and "event_id" in result:
                    event_id = result['event_id']
                    return f"""✅ 일정이 성공적으로 생성되었습니다!

📅 일정 정보:
• 제목: {title}
• 시간: {start_at} ~ {end_at}
• 설명: {description}

🆔 이벤트 ID: `{event_id}`

💡 이 일정을 나중에 수정하거나 삭제하려면 위의 이벤트 ID를 사용하세요.
예시: "이벤트 ID {event_id}의 일정을 삭제해줘" 또는 "이벤트 ID {event_id}의 일정 제목을 변경해줘"
"""
                else:
                    return f"✅ 일정 생성 완료!\n📅 제목: {title}\n⏰ 시간: {start_at} ~ {end_at}"
                    
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

            # 입력 검증
            if not event_id or not event_id.strip():
                return "❌ 오류: 이벤트 ID가 제공되지 않았습니다. 유효한 이벤트 ID를 입력해주세요."

            try:
                result = self.calendar.get_events(event_id=event_id)

                print(f"Calendar API Response: {result}")

                if result and "event" in result:
                    event = result["event"]
                    return f"✅ 일정 정보를 찾았습니다!\n📅 일정 상세 정보: {event}"
                elif result and "events" in result and result["events"]:
                    # 여러 일정이 반환된 경우
                    events = result["events"]
                    return f"✅ {len(events)}개의 일정을 찾았습니다.\n📅 일정 목록: {events}"
                else:
                    return "❌ 해당 이벤트 ID로 일정을 찾을 수 없습니다. 이벤트 ID를 확인해주세요."

            except Exception as e:
                error_msg = f"일정 정보를 가져오는 데 실패했습니다: {str(e)}"
                print(f"Error: {error_msg}")
                return f"❌ 오류: {error_msg}"

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
                    return f"✅ 일정 수정이 완료되었습니다!\n🆔 이벤트 ID: {event_id}"
                else:
                    return "❌ 일정 수정에 실패했습니다."
                    
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
                    return f"✅ 일정 삭제가 완료되었습니다!\n🆔 삭제된 이벤트 ID: {event_id}"
                else:
                    return "❌ 일정 삭제에 실패했습니다."
                    
            except Exception as e:
                error_msg = f"일정 삭제에 실패했습니다: {str(e)}"
                print(f"Error: {error_msg}")
                return error_msg

        # 도구들 생성
        self.create_event_tool = tool(create_calendar_event_tool)
        self.get_details_event_tool = tool(get_details_event_tool)
        self.update_event_tool = tool(update_calendar_event_tool)
        self.delete_event_tool = tool(delete_calendar_event_tool)

        # 프롬프트 가져오기
        prompt = get_prompt('calendar')
        
        # React Agent 생성
        self.agent = create_react_agent(
            self.llm,
            tools=[
                self.create_event_tool,
                self.get_details_event_tool,
                self.update_event_tool,
                self.delete_event_tool,
            ],
            prompt=prompt
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