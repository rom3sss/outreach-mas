"""Lead Generation Agent with improved validation and error handling."""

import re
import logging
from typing import List, Dict, Optional
from googleapiclient.errors import HttpError

from utils.google_api_clients import get_sheets_service
from config import config


class LeadGenerationAgent:
    """Agent responsible for fetching and validating leads from Google Sheets."""
    
    def __init__(self):
        """Initialize the Lead Generation Agent."""
        self.sheets_service = get_sheets_service()
        self.spreadsheet_id = config.google_sheet_id
        self.range_name = config.SHEET_RANGE
        
        if not self.sheets_service:
            logging.error("Failed to initialize Google Sheets service")

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format using regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))

    def _validate_lead(self, row: List[str]) -> Optional[Dict[str, str]]:
        """
        Validate and clean lead data.
        
        Args:
            row: Raw row data from the spreadsheet
            
        Returns:
            Dictionary with lead data or None if invalid
        """
        if len(row) < config.MIN_ROW_LENGTH:
            logging.warning(f"Insufficient data in row: {row}")
            return None
        
        # Clean and validate email
        email = row[2].strip() if len(row) > 2 else ""
        if not self._is_valid_email(email):
            logging.warning(f"Invalid email in row: {email}")
            return None
            
        # Clean other fields
        first_name = row[0].strip() if len(row) > 0 else ""
        last_name = row[1].strip() if len(row) > 1 else ""
        company = row[3].strip() if len(row) > 3 else ""
        title = row[4].strip() if len(row) > 4 else ""
        industry = row[5].strip() if len(row) > 5 else ""
        
        # Validate required fields
        if not all([first_name, email, company]):
            logging.warning(f"Missing required fields in row: {row}")
            return None
            
        return {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "company": company,
            "title": title,
            "industry": industry
        }

    def fetch_leads(self) -> List[Dict[str, str]]:
        """
        Fetch and validate lead data from the configured Google Sheet.
        
        Returns:
            List of validated lead dictionaries
        """
        if not self.sheets_service:
            logging.error("Google Sheets service not available")
            return []
            
        try:
            logging.info(f"Fetching leads from sheet: {self.spreadsheet_id}")
            
            sheet = self.sheets_service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self.range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logging.warning("No data found in the sheet")
                return []

            # Validate and clean leads
            leads = []
            total_rows = len(values)
            
            for i, row in enumerate(values, start=2):  # Start at 2 since A2 is first data row
                lead = self._validate_lead(row)
                if lead:
                    leads.append(lead)
                else:
                    logging.warning(f"Skipped invalid row {i}: {row}")
            
            valid_count = len(leads)
            logging.info(f"Successfully processed {valid_count}/{total_rows} leads")
            
            return leads

        except HttpError as e:
            logging.error(f"HTTP error fetching leads: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error fetching leads: {e}")
            return []
