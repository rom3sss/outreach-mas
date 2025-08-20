"""Google API client utilities with improved error handling and logging."""

import os
import pickle
import logging
from typing import Optional
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import config

# Define the scopes needed for the application
SCOPES_GMAIL = [
    'https://www.googleapis.com/auth/gmail.send', 
    'https://www.googleapis.com/auth/gmail.readonly'
]
SCOPES_SHEETS = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def get_google_api_service(service_name: str, scopes: list) -> Optional[object]:
    """
    Creates and returns a Google API service object.
    Handles OAuth2 authentication and token management.
    
    Args:
        service_name: Name of the service ('gmail' or 'sheets')
        scopes: List of OAuth2 scopes required
        
    Returns:
        Google API service object or None if failed
    """
    creds = None
    token_filename = f'token_{service_name}.pickle'

    try:
        # Load existing credentials
        if os.path.exists(token_filename):
            with open(token_filename, 'rb') as token:
                creds = pickle.load(token)
                logging.debug(f"Loaded existing credentials for {service_name}")

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logging.info(f"Refreshing expired credentials for {service_name}")
                creds.refresh(Request())
            else:
                logging.info(f"Starting OAuth flow for {service_name}")
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.google_credentials_path, scopes)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_filename, 'wb') as token:
                pickle.dump(creds, token)
                logging.info(f"Saved new credentials for {service_name}")
                
        # Build the service
        if service_name == 'gmail':
            service = build('gmail', 'v1', credentials=creds)
        elif service_name == 'sheets':
            service = build('sheets', 'v4', credentials=creds)
        else:
            raise ValueError(f"Unsupported service name: {service_name}")
        
        logging.info(f"Successfully created {service_name} service")
        return service
        
    except FileNotFoundError as e:
        logging.error(f"Credentials file not found: {e}")
        return None
    except HttpError as e:
        logging.error(f"HTTP error creating {service_name} service: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error creating {service_name} service: {e}")
        return None


def get_gmail_service() -> Optional[object]:
    """Convenience function to get the Gmail service."""
    return get_google_api_service('gmail', SCOPES_GMAIL)


def get_sheets_service() -> Optional[object]:
    """Convenience function to get the Sheets service."""
    return get_google_api_service('sheets', SCOPES_SHEETS)
