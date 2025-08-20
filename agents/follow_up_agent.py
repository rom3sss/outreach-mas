"""Follow-up Agent with improved error handling and logging."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from googleapiclient.errors import HttpError

from utils.google_api_clients import get_gmail_service
from config import config


class FollowUpAgent:
    """Agent responsible for managing follow-up logic and reply detection."""
    
    def __init__(self):
        """Initialize the Follow-up Agent."""
        self.gmail_service = get_gmail_service()
        self.follow_up_delay = config.follow_up_delay_hours
        
        if not self.gmail_service:
            logging.error("Failed to initialize Gmail service")

    def check_for_reply(self, lead_email: str, after_timestamp: str) -> bool:
        """
        Check for a reply from a specific email address after a given timestamp.
        
        Args:
            lead_email: Email address to check for replies from
            after_timestamp: ISO 8601 timestamp string to check after
            
        Returns:
            True if a reply was found, False otherwise
        """
        if not self.gmail_service:
            logging.error("Gmail service not available for reply checking")
            return False
            
        try:
            # Convert ISO 8601 string timestamp to Unix timestamp
            after_dt = datetime.fromisoformat(after_timestamp.replace('Z', '+00:00'))
            after_unix_ts = int(after_dt.timestamp())
            
            # Search for messages from the lead after the timestamp
            query = f"from:{lead_email} after:{after_unix_ts}"
            results = self.gmail_service.users().messages().list(
                userId='me', 
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            reply_count = len(messages)
            
            if reply_count > 0:
                logging.info(f"Found {reply_count} reply(s) from {lead_email}")
                return True
            else:
                logging.debug(f"No replies found from {lead_email}")
                return False

        except ValueError as e:
            logging.error(f"Invalid timestamp format for {lead_email}: {e}")
            return False
        except HttpError as e:
            logging.error(f"HTTP error checking replies from {lead_email}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error checking replies from {lead_email}: {e}")
            return False

    def should_send_follow_up(self, initial_email_sent_timestamp: str) -> bool:
        """
        Determine if enough time has passed to send a follow-up.
        
        Args:
            initial_email_sent_timestamp: ISO 8601 timestamp when initial email was sent
            
        Returns:
            True if it's time to send a follow-up, False otherwise
        """
        try:
            sent_time = datetime.fromisoformat(
                initial_email_sent_timestamp.replace('Z', '+00:00')
            )
            current_time = datetime.now(timezone.utc)
            follow_up_time = sent_time + timedelta(hours=self.follow_up_delay)
            
            should_send = current_time >= follow_up_time
            
            if should_send:
                hours_passed = (current_time - sent_time).total_seconds() / 3600
                logging.info(f"Follow-up time reached ({hours_passed:.1f} hours passed)")
            else:
                hours_remaining = (follow_up_time - current_time).total_seconds() / 3600
                logging.debug(f"Follow-up not due yet ({hours_remaining:.1f} hours remaining)")
                
            return should_send
            
        except ValueError as e:
            logging.error(f"Invalid timestamp format: {e}")
            return False
        except Exception as e:
            logging.error(f"Error calculating follow-up timing: {e}")
            return False
