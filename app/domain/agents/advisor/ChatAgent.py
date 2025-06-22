from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.config.ai import openai_chat
from app.config.settings import get_settings

settings = get_settings()

class ChatAgent:
    def __init__(self, llm = None):
        self.llm = llm or openai_chat
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 친근하고 도움이 되는 AI 어시스턴트입니다. 
사용자와 자연스럽게 대화하며, 질문에 답하고 도움을 제공합니다.
특별한 도구나 기능이 필요하지 않은 일반적인 대화를 담당합니다.

🛡️ 신뢰성 및 정확성 원칙:
- 절대로 확실하지 않은 정보를 제공하지 마세요
- 사실에 기반한 정보만을 제공하세요
- 추측이나 가정을 바탕으로 한 정보는 제공하지 마세요
- "모르겠습니다" 또는 "확인할 수 없습니다"라고 솔직히 말하세요
- 의학, 법률, 재정 등 전문적인 조언이 필요한 경우 전문가를 찾으라고 안내하세요
- 최신 정보가 필요한 경우 검색을 권장하세요

💡 대화 가이드라인:
- 항상 친근하고 정중하게 응답하세요
- 사용자의 질문을 정확히 이해하고 답변하세요
- 복잡한 주제는 단계별로 설명하세요
- 사용자가 이해하기 쉽도록 예시를 들어 설명하세요
- 위험하거나 부적절한 요청에는 거절하고 이유를 설명하세요

항상 친근하고 정중하게 응답하세요."""),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        self.chain = self.prompt | self.llm
    
    def invoke(self, state):
        """그래프에서 호출되는 메서드"""
        try:
            # 메시지 추출
            messages = state.get("messages", [])
            
            # agent_scratchpad가 없으면 빈 리스트로 설정
            agent_scratchpad = state.get("agent_scratchpad", [])
            
            # 체인 실행
            result = self.chain.invoke({
                "messages": messages,
                "agent_scratchpad": agent_scratchpad
            })
            
            # 응답 반환
            return {
                "messages": [result]
            }
        except Exception as e:
            error_msg = f"대화 처리 중 오류가 발생했습니다: {str(e)}"
            print(f"ChatAgent Error: {error_msg}")
            return {
                "messages": [error_msg]
            }