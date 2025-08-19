# agents/sending_agent.py


import os
import base64
from email.mime.text import MIMEText
from utils.google_api_clients import get_gmail_service


class SendingAgent:
    def __init__(self):
        self.gmail_service = get_gmail_service()
        self.sender_email = os.getenv('SENDER_EMAIL')


    def send_email(self, recipient_email: str, subject: str, body: str) -> bool:
        """
        Sends an email using the Gmail API.
        """
        if not self.gmail_service:
            print("Gmail service is not available. Cannot send email.")
            return False
            
        try:
            message = MIMEText(body)
            message['to'] = recipient_email
            message['from'] = self.sender_email
            message['subject'] = subject


            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            body = {'raw': raw_message}
            
            self.gmail_service.users().messages().send(
                userId='me', body=body
            ).execute()
            
            print(f"Email successfully sent to {recipient_email}")
            return True


        except Exception as e:
            print(f"Failed to send email to {recipient_email}. Error: {e}")
            return False