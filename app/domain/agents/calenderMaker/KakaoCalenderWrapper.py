import requests
from pydantic import BaseModel

from app.config.settings import settings


class KakaoCalenderWrapper(BaseModel):

    auth_token: str = "Bearer"+settings.KAKAO_KEY

    def results(self, title: str, description: str, strat_at: str, end_at: str) -> dict:
        return self._kakao_calender_create_results(
            title=title,
            description=description,
            strat_at=strat_at,
            end_at=end_at
        )

    def run(self, title: str, description: str, strat_at: str, end_at: str) -> str:
        results = self._kakao_calender_create_results(
            title=title,
            description=description,
            strat_at=strat_at,
            end_at=end_at
        )
        return self._parse_results(results)

    def _parse_results(self, results: dict) -> str:
        return results["event_id"]

    def _kakao_calender_create_results(self, title:str, description: str, strat_at: str, end_at: str, all_day:str = False, lunar: str = False) -> dict:
        """Create Kakao Calendar event creation results"""
        url = "https://kapi.kakao.com/v2/api/calendar/create/event"
        payload = {
            "title": title,
            "time": {
                "start_at": strat_at,
                "end_at": end_at,
                "all_day": all_day,
                "lunar": lunar
            },
            "description": description
        }

        headers = {
            "Authorization": self.auth_token
        }
        params = {
            "event": payload
        }

        response = requests.post(
            url, headers=headers, params=params
        )
        response.raise_for_status()
        search_results = response.json()
        return search_results