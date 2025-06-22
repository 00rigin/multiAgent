from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

class MailInterface(ABC):
    """
    Simple Mail service interface for email operations.
    """
    
    @abstractmethod
    def send_email(self, to: List[str], subject: str, body: str) -> Dict[str, Any]:
        """
        Send an email.
        
        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body content
            cc: List of CC recipients (optional)
            bcc: List of BCC recipients (optional)
            
        Returns:
            API response as dictionary
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test the connection to mail service.
        
        Returns:
            True if connection is successful, False otherwise
        """
        pass 