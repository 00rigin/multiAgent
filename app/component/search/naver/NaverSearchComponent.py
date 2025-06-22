from typing import Any, List

import requests
from pydantic.main import BaseModel
from typing_extensions import Literal

from app.component.search.SearchInterface import SearchInterface
from app.config.settings import settings


class NaverSearchComponent(BaseModel, SearchInterface):
    """
    네이버 검색 API를 사용하는 검색 컴포넌트
    """
    display: int = 5
    start: int = 1
    sort: str = "date"
    type: Literal["news", "blog", "webkr", "kin", "doc"] = "kin"

    X_Naver_Client_Id: str = settings.NAVER_CLIENT_ID
    X_Naver_Client_Secret: str = settings.NAVER_CLIENT_SECRET

    class Config:
        arbitrary_types_allowed = True

    def search(self, query: str, **kwargs: Any) -> str:
        """
        네이버 검색 API를 사용하여 검색을 수행하고 결과를 반환합니다.
        
        Args:
            query: 검색 쿼리
            **kwargs: 추가 검색 옵션들
            
        Returns:
            검색 결과 문자열
        """
        results = self._naver_search_api_results(
            search_term=query,
            display=self.display,
            start=self.start,
            sort=self.sort,
            search_type=self.type,
            **kwargs,
        )
        return self._parse_results(results)

    def _parse_descriptions(self, results: dict) -> List[str]:
        """검색 결과에서 description을 추출합니다."""
        descriptions = []
        for result in results["items"]:
            if "description" in result:
                descriptions.append(result["description"])

        if len(descriptions) == 0:
            return ["No good Naver Search Result was found"]
        return descriptions

    def _parse_results(self, results: dict) -> str:
        """검색 결과를 파싱하여 문자열로 반환합니다."""
        result = " ".join(self._parse_descriptions(results))
        return result

    def _naver_search_api_results(
        self, search_term: str, search_type: str = "kin", **kwargs: Any
    ) -> dict:
        """
        네이버 검색 API를 호출합니다.
        
        Args:
            search_term: 검색어
            search_type: 검색 타입
            **kwargs: 추가 파라미터
            
        Returns:
            API 응답 결과
        """
        headers = {
            "X-Naver-Client-Id": self.X_Naver_Client_Id,
            "X-Naver-Client-Secret": self.X_Naver_Client_Secret
        }
        params = {
            "query": search_term,
            **{key: value for key, value in kwargs.items() if value is not None},
        }
        response = requests.get(
            f"https://openapi.naver.com/v1/search/{search_type}.json", 
            headers=headers, 
            params=params
        )
        response.raise_for_status()
        search_results = response.json()
        return search_results 