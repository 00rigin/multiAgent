from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
from typing import Optional
from datetime import datetime

from app.config.ai import openai_chat
from app.component.search.SearchInterface import SearchInterface
from app.component.search.naver.NaverSearchComponent import NaverSearchComponent
from app.config.prompts import get_prompt


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

        # 프롬프트 가져오기
        prompt = get_prompt('search')
        
        # React Agent 생성
        self.agent = create_react_agent(
            self.llm,
            tools=[self.search_tool],
            prompt=prompt
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