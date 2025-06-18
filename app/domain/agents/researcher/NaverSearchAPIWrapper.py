from typing import Any, Dict, List, Optional

import aiohttp
import requests
from pydantic.main import BaseModel
from typing_extensions import Literal

from app.config.settings import settings


class NaverSearchAPIWrapper(BaseModel):
    display: int = 5
    start: int = 1
    sort: str = "date"
    type: Literal["news" ,"blog" ,"webkr" ,"kin" ,"doc"] = "kin"

    X_Naver_Client_Id: str = settings.NAVER_CLIENT_ID
    X_Naver_Client_Secret: str = settings.NAVER_CLIENT_SECRET

    aiosession: Optional[aiohttp.ClientSession] = None

    class Config:
        arbitrary_types_allowed = True

    def results(self, query :str, **kwargs: Any) -> Dict:
        return self._naver_search_api_results(
            search_term = query,
            display= self.display,
            start = self.start,
            sort = self.sort,
            search_type=self.type,
            **kwargs,
        )

    def run(self, query: str, **kwargs: Any) -> str:
        results = self._naver_search_api_results(
            search_term = query,
            display= self.display,
            start = self.start,
            sort = self.sort,
            search_type=self.type,
            **kwargs,
        )
        return self._parse_results(results)

    def _parse_descriptions(self, results: dict) -> List[str] :
        descriptions = []
        for result in results["items"]:
            if "description" in result:
                descriptions.append(result["description"])

        if len(descriptions) == 0:
            return ["No good Naver Search Result was found"]
        return descriptions

    def _parse_results(self, results: dict) -> str:
        result = " ".join(self._parse_descriptions(results))
        return result

    def _naver_search_api_results(
            self, search_term: str, search_type: str = "kin", **kwargs: Any
    ) -> dict:
        headers = {
            "X-Naver-Client-Id" : self.X_Naver_Client_Id,
            "X-Naver-Client-Secret" : self.X_Naver_Client_Secret
        }
        params = {
            "query" : search_term,
            **{key: value for key, value in kwargs.items() if value is not None},
        }
        response = requests.get(
            f"https://openapi.naver.com/v1/search/{search_type}.json", headers=headers, params=params
        )
        response.raise_for_status()
        search_results = response.json()
        return search_results

search = NaverSearchAPIWrapper()