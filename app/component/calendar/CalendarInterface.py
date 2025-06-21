from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class CalendarInterface(ABC):
    """
    Calendar service interface for different calendar providers.
    All calendar implementations must implement these methods.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event.
        
        Args:
            event_id: Event ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test the connection to calendar API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        pass 