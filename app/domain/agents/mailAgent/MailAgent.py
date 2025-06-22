from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
from typing import Optional

from app.config.ai import openai_chat
from app.component.mail.MailInterface import MailInterface
from app.component.mail.gmail.GmailComponent import GmailComponent
from app.config.prompts import get_prompt


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
            # Default to Gmail
            self.mail = GmailComponent()

        def send_email_tool(to: str, subject: str, body: str) -> str:
            """
            Send an email using the mail component.
            
            Args:
                to: 수신자 이메일 주소 (쉼표로 구분된 여러 주소 지원)
                subject: 이메일 제목
                body: 이메일 내용
            """
            print("============ Send Email ===============")
            print(f"To: {to}")
            print(f"Subject: {subject}")
            print(f"Body: {body}")
            
            try:
                # 쉼표로 구분된 이메일 주소를 리스트로 변환
                to_list = [email.strip() for email in to.split(',')]
                
                result = self.mail.send_email(to=to_list, subject=subject, body=body)
                
                print(f"Mail API Response: {result}")
                
                if result and "message_id" in result:
                    message_id = result['message_id']
                    return f"""✅ 이메일이 성공적으로 발송되었습니다!

📧 이메일 정보:
• 수신자: {to}
• 제목: {subject}
• 내용: {body[:100]}{'...' if len(body) > 100 else ''}

🆔 메시지 ID: `{message_id}`

💡 이메일 발송이 완료되었습니다."""
                else:
                    return f"✅ 이메일 발송 완료!\n📧 수신자: {to}\n📝 제목: {subject}"
                    
            except Exception as e:
                error_msg = f"이메일 발송에 실패했습니다: {str(e)}"
                print(f"Error: {error_msg}")
                return error_msg

        # 도구들 생성
        self.send_email_tool = tool(send_email_tool)

        # 프롬프트 가져오기
        prompt = get_prompt('mail')

        # React Agent 생성
        self.agent = create_react_agent(
            self.llm,
            tools=[
                self.send_email_tool,
            ],
            prompt=prompt
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