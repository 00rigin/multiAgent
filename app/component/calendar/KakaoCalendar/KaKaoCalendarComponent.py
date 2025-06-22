import requests
from typing import Optional, Dict, Any
import json
from datetime import datetime
from app.config.settings import settings
from app.component.calendar.CalendarInterface import CalendarInterface

class KakaoCalendarComponent(CalendarInterface):
    """
    Kakao Calendar Component for managing calendar events.
    Spring Boot style component that handles all Kakao Calendar API communications.
    """
    
    def __init__(self, auth_token: Optional[str] = None):
        """
        Initialize Kakao Calendar Component.
        
        Args:
            auth_token: Optional custom auth token (defaults to settings.KAKAO_KEY)
        """
        self.auth_token = auth_token or f"Bearer {settings.KAKAO_KEY}"
        self.base_url = "https://kapi.kakao.com/v2/api/calendar"
        self.headers = {
            "Authorization": self.auth_token
        }
    
    def create_event(self, title: str, description: str, start_at: str, end_at: str) -> Dict[str, Any]:
        """
        Create a new calendar event.
        
        Args:
            title: Event title
            description: Event description
            start_at: Start time (ISO 8601 format)
            end_at: End time (ISO 8601 format)
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/create/event"
        
        # 이벤트 데이터 구성
        event_data = {
            "title": title,
            "time": {
                "start_at": start_at,
                "end_at": end_at
            },
            "description": description
        }
    
        
        # form-data 방식으로 전송 (공식 문서와 동일)
        data = {
            "event": json.dumps(event_data)  # JSON 문자열로 변환
        }
        
        try:
            response = requests.post(
                url, 
                headers=self.headers, 
                data=data,  # form-data 방식
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create calendar event: {str(e)}")

    def get_events(self,
                   event_id: str) -> Dict[str, Any]:
        """
        Get calendar events.

        Args:
            event_id: Event ID

        Returns:
            Event details as dictionary
        """
        url = f"{self.base_url}/event"

        params = {
            "event_id": event_id
        }

        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get calendar events: {str(e)}")
    
    def update_event(self, event_id: str, title: Optional[str] = None, 
                    description: Optional[str] = None, start_at: Optional[str] = None,
                    end_at: Optional[str] = None, all_day: Optional[bool] = None) -> Dict[str, Any]:
        """
        Update an existing calendar event.
        
        Args:
            event_id: Event ID to update
            title: New title (optional)
            description: New description (optional)
            start_at: New start time (optional)
            end_at: New end time (optional)
            all_day: Whether it's an all-day event (optional)
            
        Returns:
            Updated event as dictionary
        """
        url = f"{self.base_url}/update/event/host"
        
        payload = {
        }

        if title:
            payload["title"] = title
        if description:
            payload["description"] = description
        if start_at or end_at is not None:
            payload["time"] = {}
            if start_at:
                payload["time"]["start_at"] = start_at
            if end_at:
                payload["time"]["end_at"] = end_at

        data = {
            "event_id": event_id,
            "event": json.dumps(payload)
        }

        try:
            response = requests.post(
                url, 
                headers=self.headers, 
                data=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to update calendar event: {str(e)}")
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event.
        
        Args:
            event_id: Event ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/delete/event"
        
        params = {
            "event_id": event_id
        }
        
        try:
            response = requests.delete(
                url, 
                headers=self.headers,
                params=params,  # query parameter 방식
                timeout=30
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to delete calendar event: {str(e)}")
    
    