"""Configuration management for the multi-agent outreach system."""

import os
import logging
from typing import List
from dotenv import load_dotenv


class Config:
    """Centralized configuration management with validation."""
    
    # Constants
    DEFAULT_FOLLOW_UP_DELAY = 48
    SHEET_RANGE = 'Lead Sheet!A2:F'
    MIN_ROW_LENGTH = 6
    
    def __init__(self):
        """Initialize configuration and validate required variables."""
        load_dotenv()
        self._validate_required_vars()
        
    def _validate_required_vars(self) -> None:
        """Validate that all required environment variables are set."""
        required = [
            'GOOGLE_API_KEY',
            'GOOGLE_SHEET_ID', 
            'SENDER_EMAIL',
            'YOUR_NAME',
            'YOUR_TITLE',
            'BIGQUERY_PROJECT_ID'
        ]
        
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")
            
        logging.info("All required environment variables are present")
    
    @property
    def google_api_key(self) -> str:
        """Get Google API key."""
        return os.getenv('GOOGLE_API_KEY')
    
    @property
    def google_sheet_id(self) -> str:
        """Get Google Sheet ID."""
        return os.getenv('GOOGLE_SHEET_ID')
    
    @property
    def sender_email(self) -> str:
        """Get sender email address."""
        return os.getenv('SENDER_EMAIL')
    
    @property
    def your_name(self) -> str:
        """Get your name."""
        return os.getenv('YOUR_NAME')
    
    @property
    def your_title(self) -> str:
        """Get your title."""
        return os.getenv('YOUR_TITLE')
    
    @property
    def portfolio_link(self) -> str:
        """Get portfolio link."""
        return os.getenv('PORTFOLIO_LINK', '[Link to Portfolio/Showreel]')
    
    @property
    def follow_up_delay_hours(self) -> int:
        """Get follow-up delay in hours."""
        return int(os.getenv('FOLLOW_UP_DELAY_HOURS', self.DEFAULT_FOLLOW_UP_DELAY))
    
    @property
    def google_credentials_path(self) -> str:
        """Get Google credentials file path."""
        return os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
    
    @property
    def bigquery_project_id(self) -> str:
        """Get BigQuery project ID."""
        return os.getenv('BIGQUERY_PROJECT_ID')
    
    @property
    def bigquery_dataset_id(self) -> str:
        """Get BigQuery dataset ID."""
        return os.getenv('BIGQUERY_DATASET_ID', 'outreach_analytics')
    
    @property
    def bigquery_location(self) -> str:
        """Get BigQuery location."""
        return os.getenv('BIGQUERY_LOCATION', 'US')


# Global config instance
config = Config()
