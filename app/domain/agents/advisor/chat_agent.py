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
            return {
                "messages": [f"대화 처리 중 오류가 발생했습니다: {str(e)}"]
            }