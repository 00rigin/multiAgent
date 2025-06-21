from langgraph.prebuilt import create_react_agent
from langchain_core.tools import Tool

from app.config.ai import openai_chat
from app.domain.agents.researcher.NaverSearchAPIWrapper import NaverSearchAPIWrapper

class SearchAgent:

    def __init__(
        self,
        llm = None,
        display: int = 5,
        start: int = 1,
        sort: str = "date"
    ):
        # 1) 네이버 검색 래퍼 초기화
        self.llm = llm or openai_chat
        self.wrapper = NaverSearchAPIWrapper(
            display=display,
            start=start,
            sort=sort
        )

        # 2) 툴 정의: 동기 검색 함수를 별도로 정의
        def naver_search_tool(query: str) -> str:
            """Tool 내부에서 호출되는 동기 검색 메서드"""
            return self.wrapper.run(query)

        self.search_tool = Tool(
            name="naver_search",
            func=naver_search_tool,
            description=(
                "네이버 OpenAPI로 검색을 수행합니다."
                " 입력(query: str) → 검색 결과 description 합쳐서 반환"
            ),
        )

        # 3) React Agent 생성 (AgentExecutor 없이)
        self.agent = create_react_agent(
            self.llm,
            tools=[self.search_tool],
            prompt= "You are a helpful search agent that uses the Naver OpenAPI to find information."
        )
