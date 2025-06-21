from typing import Optional, Dict, Any

import requests

from app.component.calendar.KaKaoCalendarComponent import KakaoCalendarComponent
from app.config.settings import settings


class KakaoTalkComponent:
    def __init__(self, auth_token: Optional[str] = None):
        """
        Initialize Kakao talk Component.

        Args:
            auth_token: Optional custom auth token (defaults to settings.KAKAO_KEY)
        """
        self.auth_token = auth_token or f"Bearer {settings.KAKAO_KEY}"
        self.base_url = "https://kapi.kakao.com/v1/api/talk"
        self.headers = {
            "Authorization": self.auth_token
        }

    def get_friends(self) -> Dict[str, Any]:
        """
        Get the list of friends from Kakao Talk.

        Returns:
            API response as dictionary containing friends list
        """
        url = f"{self.base_url}/friends"
        params = {
            "order": "asc",
            "friend_order" : "favorite"
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to find friends: {str(e)}")

    def send_calendar(self, receiver_uuids: str, event_id: str) -> Dict[str, Any]:
        """
        Send a calendar event to a friend.

        Args:
            friend_id: The ID of the friend to send the event to
            event_id: The ID of the calendar event to send

        Returns:
            API response as dictionary
        """

        calendar = KakaoCalendarComponent()
        event_info = calendar.get_events(event_id)
        if not event_info:
            raise ValueError(f"Event with ID {event_id} does not exist.")



        url = f"{self.base_url}/send_calendar"
        data = {
            "receiver_uuids ": list(receiver_uuids) ,
            "event_id": event_id
        }

        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to send calendar event: {str(e)}")