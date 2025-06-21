from pydantic import BaseModel
import requests
from typing import Optional, Dict, Any
import json
from datetime import datetime

class KakaoCalendarComponent(BaseModel):
    """
    Kakao Calendar Component for managing calendar events.
    Spring Boot style component that handles all Kakao Calendar API communications.
    """
    
    auth_token: str
    base_url: str = "https://kapi.kakao.com/v2/api/calendar"
    
    def __init__(self, auth_token: str):
        super().__init__(auth_token=auth_token)
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def create_event(self, title: str, description: str, start_at: str, end_at: str, 
                    all_day: bool = False, lunar: bool = False) -> Dict[str, Any]:
        """
        Create a new calendar event.
        
        Args:
            title: Event title
            description: Event description
            start_at: Start time (ISO 8601 format)
            end_at: End time (ISO 8601 format)
            all_day: Whether it's an all-day event
            lunar: Whether to use lunar calendar
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/create/event"
        
        payload = {
            "title": title,
            "time": {
                "start_at": start_at,
                "end_at": end_at,
                "all_day": all_day,
                "lunar": lunar
            },
            "description": description
        }
        
        try:
            response = requests.post(
                url, 
                headers=self.headers, 
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create calendar event: {str(e)}")
    
    def get_events(self, calendar_id: Optional[str] = None, 
                  start_date: Optional[str] = None, 
                  end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get calendar events.
        
        Args:
            calendar_id: Calendar ID (optional)
            start_date: Start date filter (ISO 8601 format)
            end_date: End date filter (ISO 8601 format)
            
        Returns:
            List of events as dictionary
        """
        url = f"{self.base_url}/events"
        
        params = {}
        if calendar_id:
            params["calendar_id"] = calendar_id
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
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
        url = f"{self.base_url}/update/event/{event_id}"
        
        payload = {}
        if title:
            payload["title"] = title
        if description:
            payload["description"] = description
        if start_at or end_at or all_day is not None:
            payload["time"] = {}
            if start_at:
                payload["time"]["start_at"] = start_at
            if end_at:
                payload["time"]["end_at"] = end_at
            if all_day is not None:
                payload["time"]["all_day"] = all_day
        
        try:
            response = requests.put(
                url, 
                headers=self.headers, 
                json=payload,
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
        url = f"{self.base_url}/delete/event/{event_id}"
        
        try:
            response = requests.delete(
                url, 
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to delete calendar event: {str(e)}")
    
    def get_calendars(self) -> Dict[str, Any]:
        """
        Get list of available calendars.
        
        Returns:
            List of calendars as dictionary
        """
        url = f"{self.base_url}/calendars"
        
        try:
            response = requests.get(
                url, 
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get calendars: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test the connection to Kakao Calendar API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.get_calendars()
            return True
        except Exception:
            return False
