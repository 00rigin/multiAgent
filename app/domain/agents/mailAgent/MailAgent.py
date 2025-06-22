from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
from typing import Optional

from app.config.ai import openai_chat
from app.component.mail.gmail.GmailComponent import GmailComponent
from app.component.mail.MailInterface import MailInterface


class MailAgent:
    def __init__(self, llm=None, mail_component: Optional[MailInterface] = None):
        """
        Initialize MailAgent with optional mail component.
        
        Args:
            llm: Language model to use
            mail_component: Mail implementation (defaults to GmailComponent)
        """
        self.llm = llm or openai_chat
        
        # Mail component initialization
        if mail_component:
            self.mail = mail_component
        else:
            # Default to Gmail Component
            self.mail = GmailComponent()

        def send_email_tool(to: str, subject: str, body: str) -> str:
            """
            Send an email to specified recipients.
            
            Args:
                to: 수신자 이메일 주소 (쉼표로 구분된 여러 주소 가능)
                subject: 이메일 제목
                body: 이메일 내용
            """
            print("============ Send Email ===============")
            print(f"To: {to}")
            print(f"Subject: {subject}")
            print(f"Body: {body}")
            
            try:
                to_list = [email.strip() for email in to.split(',')]
                
                result = self.mail.send_email(
                    to=to_list, subject=subject, body=body
                )
                
                print(f"Mail API Response: {result}")
                
                if result and "id" in result:
                    return f"이메일 발송 성공: {subject} - 메시지 ID: {result['id']}"
                else:
                    return f"이메일 발송 성공: {subject}"
                    
            except Exception as e:
                error_msg = f"이메일 발송에 실패했습니다: {str(e)}"
                print(f"Error: {error_msg}")
                return error_msg

        def test_connection_tool() -> str:
            """
            Test connection to Gmail API.
            """
            print("============ Test Gmail Connection ===============")
            
            try:
                success = self.mail.test_connection()
                
                print(f"Connection test result: {success}")
                
                if success:
                    return "Gmail API 연결 성공"
                else:
                    return "Gmail API 연결 실패"
                    
            except Exception as e:
                error_msg = f"연결 테스트에 실패했습니다: {str(e)}"
                print(f"Error: {error_msg}")
                return error_msg

        # 도구들 생성
        self.send_email_tool = tool(send_email_tool)
        self.test_connection_tool = tool(test_connection_tool)

        # React Agent 생성
        self.agent = create_react_agent(
            self.llm,
            tools=[
                self.send_email_tool,
                self.test_connection_tool,
            ],
            prompt="""너는 사용자의 요청을 받아 이메일을 관리하는 에이전트야.

🛡️ 신뢰성 및 정확성 원칙:
- 절대로 확실하지 않은 정보를 제공하지 마세요
- 도구 실행 결과만을 기반으로 응답하세요
- API 응답이 실패하면 정확한 오류 메시지를 전달하세요
- 추측이나 가정을 바탕으로 한 정보는 제공하지 마세요
- "모르겠습니다" 또는 "확인할 수 없습니다"라고 솔직히 말하세요
- 이메일 발송 전에 수신자, 제목, 내용이 모두 유효한지 확인하세요

주요 기능:
1. 이메일 발송: 지정된 수신자에게 이메일을 발송

사용 가능한 도구들:
- send_email_tool: 이메일 발송

💡 이메일 발송 시 주의사항:
- 수신자(to)는 쉼표로 구분된 여러 이메일 주소를 지원
- 제목(subject)과 내용(body)은 명확하게 작성
- 이메일 주소 형식이 올바른지 검증하세요
- API 호출이 실패하면 구체적인 오류 원인을 사용자에게 알려주세요

사용자의 요청을 분석하여 무언갈 외부에 공유 한다던가, 메일을 보내려고 하는 것이 있다면 send_email_tool을 사용해줘.
도구 사용에 성공 했을때, 도구 사용 결과와 key를 반환해줘.
"""
        )
    
    def run(self, message: str) -> str:
        """
        Run the mail agent with a user message.
        
        Args:
            message: User's message requesting mail operations
            
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