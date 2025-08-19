# utils/google_api_clients.py


import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Define the scopes needed for the application
SCOPES_GMAIL = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']
SCOPES_SHEETS = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def get_google_api_service(service_name, scopes):
    """
    Creates and returns a Google API service object.
    Handles OAuth2 authentication and token management.
    """
    creds = None
    token_filename = f'token_{service_name}.pickle'


    # The file token.pickle stores the user's access and refresh tokens.
    if os.path.exists(token_filename):
        with open(token_filename, 'rb') as token:
            creds = pickle.load(token)


    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv('GOOGLE_CREDENTIALS_PATH'), scopes)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_filename, 'wb') as token:
            pickle.dump(creds, token)
            
    try:
        if service_name == 'gmail':
            service = build('gmail', 'v1', credentials=creds)
        elif service_name == 'sheets':
            service = build('sheets', 'v4', credentials=creds)
        else:
            raise ValueError("Unsupported service name")
        
        print(f"Successfully authenticated and created service for: {service_name.capitalize()}")
        return service
    except Exception as e:
        print(f"An error occurred while creating the {service_name} service: {e}")
        return None


def get_gmail_service():
    """Convenience function to get the Gmail service."""
    return get_google_api_service('gmail', SCOPES_GMAIL)


def get_sheets_service():
    """Convenience function to get the Sheets service."""
    return get_google_api_service('sheets', SCOPES_SHEETS)