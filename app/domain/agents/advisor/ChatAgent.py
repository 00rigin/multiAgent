from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.config.ai import openai_chat
from app.config.settings import get_settings
from app.config.prompts import get_prompt

settings = get_settings()

class ChatAgent:
    def __init__(self, llm = None):
        self.llm = llm or openai_chat
        
        # 프롬프트 가져오기
        system_prompt = get_prompt('chat')
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
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