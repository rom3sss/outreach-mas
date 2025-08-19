# agents/follow_up_agent.py


import os
from datetime import datetime, timedelta, timezone
from utils.google_api_clients import get_gmail_service


class FollowUpAgent:
    def __init__(self):
        self.gmail_service = get_gmail_service()
        self.follow_up_delay = int(os.getenv('FOLLOW_UP_DELAY_HOURS', 48))


    def check_for_reply(self, lead_email: str, after_timestamp: str) -> bool:
        """
        Checks for a reply from a specific email address after a given timestamp.
        """
        try:
            # Convert ISO 8601 string timestamp to Unix timestamp
            after_dt = datetime.fromisoformat(after_timestamp.replace('Z', '+00:00'))
            after_unix_ts = int(after_dt.timestamp())
            
            query = f"from:{lead_email} after:{after_unix_ts}"
            results = self.gmail_service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            return len(messages) > 0


        except Exception as e:
            print(f"Error checking for replies from {lead_email}: {e}")
            return False # Assume no reply on error


    def should_send_follow_up(self, initial_email_sent_timestamp: str) -> bool:
        """
        Determines if enough time has passed to send a follow-up.
        """
        sent_time = datetime.fromisoformat(initial_email_sent_timestamp.replace('Z', '+00:00'))
        return datetime.now(timezone.utc) >= (sent_time + timedelta(hours=self.follow_up_delay))