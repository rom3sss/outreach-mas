"""Sending Agent with improved error handling and logging."""

import base64
import logging
from typing import Optional
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError

from utils.google_api_clients import get_gmail_service
from config import config


class SendingAgent:
    """Agent responsible for sending emails via Gmail API."""
    
    def __init__(self):
        """Initialize the Sending Agent."""
        self.gmail_service = get_gmail_service()
        self.sender_email = config.sender_email
        
        if not self.gmail_service:
            logging.error("Failed to initialize Gmail service")

    def send_email(self, recipient_email: str, subject: str, body: str) -> bool:
        """
        Send an email using the Gmail API.
        
        Args:
            recipient_email: Email address of the recipient
            subject: Email subject line
            body: Email body content
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.gmail_service:
            logging.error("Gmail service is not available. Cannot send email")
            return False
            
        if not all([recipient_email, subject, body]):
            logging.error("Missing required email parameters")
            return False
            
        try:
            # Create the email message
            message = MIMEText(body)
            message['to'] = recipient_email
            message['from'] = self.sender_email
            message['subject'] = subject

            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            email_body = {'raw': raw_message}
            
            # Send the email
            result = self.gmail_service.users().messages().send(
                userId='me', 
                body=email_body
            ).execute()
            
            message_id = result.get('id')
            logging.info(f"Email successfully sent to {recipient_email} (ID: {message_id})")
            return True

        except HttpError as e:
            logging.error(f"HTTP error sending email to {recipient_email}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error sending email to {recipient_email}: {e}")
            return False
