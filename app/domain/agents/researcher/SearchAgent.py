from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
from typing import Optional
from datetime import datetime

from app.config.ai import openai_chat
from app.component.search.SearchInterface import SearchInterface
from app.component.search.naver.NaverSearchComponent import NaverSearchComponent


class SearchAgent:
    def __init__(
        self,
        llm=None,
        search_component: Optional[SearchInterface] = None,
        display: int = 5,
        start: int = 1,
        sort: str = "date"
    ):
        """
        Initialize SearchAgent with optional search component.
        
        Args:
            llm: Language model to use
            search_component: Search implementation (defaults to NaverSearchComponent)
            display: Number of search results to display
            start: Starting position for search results
            sort: Sort order for search results
        """
        self.llm = llm or openai_chat
        
        # Search component initialization
        if search_component:
            self.search_component = search_component
        else:
            # Default to Naver Search
            self.search_component = NaverSearchComponent(
                display=display,
                start=start,
                sort=sort
            )

        def search_tool(query: str) -> str:
            """
            Search for information using the search component.
            
            Args:
                query: 검색 쿼리
            """
            print("============ Search Information ===============")
            print(f"Query: {query}")
            
            try:
                result = self.search_component.search(query)
                
                print(f"Search API Response: {result}")
                
                if result and "No good" not in result:
                    return f"✅ 검색이 완료되었습니다!\n\n🔍 검색 결과:\n{result}"
                else:
                    return "❌ 검색 결과를 찾을 수 없습니다. 다른 검색어를 시도해보세요."
                    
            except Exception as e:
                error_msg = f"검색에 실패했습니다: {str(e)}"
                print(f"Error: {error_msg}")
                return f"❌ 오류: {error_msg}"

        # 도구 생성
        self.search_tool = tool(search_tool)

        # 현재 날짜 정보
        current_date = datetime.now().strftime("%Y년 %m월 %d일 (%A)")
        
        # React Agent 생성
        self.agent = create_react_agent(
            self.llm,
            tools=[self.search_tool],
            prompt=f"""너는 사용자의 요청을 받아 검색을 수행하는 에이전트야.

📅 현재 날짜: {current_date}

🛡️ 신뢰성 및 정확성 원칙:
- 절대로 확실하지 않은 정보를 제공하지 마세요
- 검색 결과만을 기반으로 응답하세요
- 검색 결과가 없으면 "검색 결과를 찾을 수 없습니다"라고 솔직히 말하세요
- 추측이나 가정을 바탕으로 한 정보는 제공하지 마세요
- "모르겠습니다" 또는 "확인할 수 없습니다"라고 솔직히 말하세요

주요 기능:
1. 정보 검색: 사용자의 질문에 대한 정보를 검색
2. 결과 요약: 검색 결과를 사용자가 이해하기 쉽게 요약
3. 정확성 확인: 검색 결과의 신뢰성을 확인

사용 가능한 도구들:
- search_tool: 정보 검색 수행

💡 검색 가이드라인:
- 사용자의 질문을 정확히 이해하고 적절한 검색어를 사용하세요
- 검색 결과를 요약하여 사용자에게 제공하세요
- 검색 결과가 부족하면 다른 검색어를 시도해보세요
- 최신 정보가 필요한 경우 검색 결과의 날짜를 확인하세요
- 검색 결과가 없으면 사용자에게 다른 검색어를 제안하세요
- 날짜 관련 검색 시 현재 날짜({current_date})를 기준으로 상대적 날짜를 계산하세요

사용자의 검색 요청을 분석하여 적절한 검색어로 검색을 수행하고 결과를 제공해주세요.
도구 사용에 성공했을 때, 도구 사용 결과를 반환해줘.
"""
        )
    
    def run(self, message: str) -> str:
        """
        Run the search agent with a user message.
        
        Args:
            message: User's message requesting search operations
            
        Returns:
            Agent's response
        """
        try:
            # Agent 실행
            result = self.agent.invoke({"input": message})
            return result["output"]
        except Exception as e:
            error_msg = f"검색 에이전트 실행 중 오류가 발생했습니다: {str(e)}"
            print(f"SearchAgent Error: {error_msg}")
            return error_msg