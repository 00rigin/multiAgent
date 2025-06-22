import base64
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.component.mail.MailInterface import MailInterface
from app.config.settings import settings


class GmailComponent(MailInterface):
    """
    Simple Gmail Component for sending emails.
    Uses Google's official Gmail API Python client.
    """
    
    # Gmail API scopes - only send permission
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self):
        """
        Initialize Gmail Component.
        
        Args:
            credentials_path: Path to credentials.json file
            token_path: Path to token.json file
        """
        self.credentials_path = settings.GOOGLE_CREDENTIAL_PATH
        self.token_path = settings.GMAIL_TOKEN_PATH
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        # If no valid credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}. "
                        "Please download credentials.json from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        try:
            # Build the Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            if not labels:
                print("No labels found.")
                return
            print("Labels:")
            for label in labels:
                print(label["name"])

        except HttpError as error:
            print(f"An error occurred in Gamil Component: {error}")
    
    def send_email(self, to: List[str], subject: str, body: str) -> Dict[str, Any]:
        """
        Send an email using Gmail API.
        
        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body content
            
        Returns:
            API response as dictionary
        """
        try:
            # Create email message
            message = MIMEMultipart()
            message['to'] = ', '.join(to)
            message['subject'] = subject

            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send email using Gmail API
            message_body = {'raw': raw_message}
            sent_message = self.service.users().messages().send(
                userId='me', body=message_body
            ).execute()
            
            return sent_message
            
        except HttpError as error:
            raise Exception(f"Failed to send email: {error}")
    
    def test_connection(self) -> bool:
        """
        Test the connection to Gmail API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to get user profile
            profile = self.service.users().getProfile(userId='me').execute()
            return True
        except Exception:
            return False 