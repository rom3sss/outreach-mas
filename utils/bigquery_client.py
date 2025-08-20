"""BigQuery client utilities for storing and analyzing outreach data."""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.oauth2.service_account import Credentials

from config import config


class BigQueryClient:
    """Client for managing BigQuery operations for outreach analytics."""
    
    def __init__(self):
        """Initialize BigQuery client with OAuth credentials."""
        try:
            # Try using OAuth credentials (same as Gmail/Sheets)
            import pickle
            import os
            from google.auth.transport.requests import Request
            from google_auth_oauthlib.flow import InstalledAppFlow
            
            # BigQuery scopes
            SCOPES = ['https://www.googleapis.com/auth/bigquery']
            
            creds = None
            token_filename = 'token_bigquery.pickle'
            
            # Load existing credentials
            if os.path.exists(token_filename):
                with open(token_filename, 'rb') as token:
                    creds = pickle.load(token)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        config.google_credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(token_filename, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.client = bigquery.Client(
                credentials=creds,
                project=config.bigquery_project_id
            )
            self.dataset_id = config.bigquery_dataset_id
            self.project_id = config.bigquery_project_id
            self.location = config.bigquery_location
            
            # Initialize dataset and tables
            self._setup_dataset_and_tables()
            logging.info("BigQuery client initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize BigQuery client: {e}")
            self.client = None
    
    def _setup_dataset_and_tables(self) -> None:
        """Create dataset and tables if they don't exist."""
        if not self.client:
            return
            
        try:
            # Create dataset if it doesn't exist
            dataset_ref = self.client.dataset(self.dataset_id)
            try:
                self.client.get_dataset(dataset_ref)
                logging.info(f"Dataset {self.dataset_id} already exists")
            except NotFound:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = self.location
                dataset.description = "Outreach analytics data"
                self.client.create_dataset(dataset)
                logging.info(f"Created dataset {self.dataset_id}")
            
            # Create tables
            self._create_leads_table()
            self._create_email_events_table()
            self._create_campaigns_table()
            
        except Exception as e:
            logging.error(f"Error setting up BigQuery dataset and tables: {e}")
    
    def _create_leads_table(self) -> None:
        """Create the leads table."""
        table_id = f"{self.project_id}.{self.dataset_id}.leads"
        
        schema = [
            bigquery.SchemaField("lead_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("first_name", "STRING"),
            bigquery.SchemaField("last_name", "STRING"),
            bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company", "STRING"),
            bigquery.SchemaField("title", "STRING"),
            bigquery.SchemaField("industry", "STRING"),
            bigquery.SchemaField("status", "STRING"),
            bigquery.SchemaField("created_at", "TIMESTAMP"),
            bigquery.SchemaField("updated_at", "TIMESTAMP"),
        ]
        
        self._create_table_if_not_exists("leads", schema)
    
    def _create_email_events_table(self) -> None:
        """Create the email events table."""
        schema = [
            bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("lead_email", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),  # INITIAL_SENT, FOLLOW_UP_SENT, REPLIED, BOUNCED
            bigquery.SchemaField("email_subject", "STRING"),
            bigquery.SchemaField("timestamp", "TIMESTAMP"),
            bigquery.SchemaField("campaign_id", "STRING"),
        ]
        
        self._create_table_if_not_exists("email_events", schema)
    
    def _create_campaigns_table(self) -> None:
        """Create the campaigns table."""
        schema = [
            bigquery.SchemaField("campaign_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("campaign_name", "STRING"),
            bigquery.SchemaField("started_at", "TIMESTAMP"),
            bigquery.SchemaField("total_leads", "INTEGER"),
            bigquery.SchemaField("emails_sent", "INTEGER"),
            bigquery.SchemaField("replies_received", "INTEGER"),
            bigquery.SchemaField("response_rate", "FLOAT"),
        ]
        
        self._create_table_if_not_exists("campaigns", schema)
    
    def _create_table_if_not_exists(self, table_name: str, schema: List[bigquery.SchemaField]) -> None:
        """Create a table if it doesn't exist."""
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        try:
            self.client.get_table(table_id)
            logging.info(f"Table {table_name} already exists")
        except NotFound:
            table = bigquery.Table(table_id, schema=schema)
            table = self.client.create_table(table)
            logging.info(f"Created table {table_name}")
    
    def insert_lead(self, lead_data: Dict[str, Any]) -> bool:
        """Insert or update lead data."""
        if not self.client:
            return False
            
        try:
            table_id = f"{self.project_id}.{self.dataset_id}.leads"
            
            # Generate lead_id from email
            lead_id = self._generate_lead_id(lead_data['email'])
            
            row = {
                "lead_id": lead_id,
                "first_name": lead_data.get('firstName', ''),
                "last_name": lead_data.get('lastName', ''),
                "email": lead_data['email'],
                "company": lead_data.get('company', ''),
                "title": lead_data.get('title', ''),
                "industry": lead_data.get('industry', ''),
                "status": lead_data.get('status', 'PENDING'),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            
            # Use MERGE to insert or update
            query = f"""
            MERGE `{table_id}` AS target
            USING (SELECT 
                "{row['lead_id']}" as lead_id,
                "{row['first_name']}" as first_name,
                "{row['last_name']}" as last_name,
                "{row['email']}" as email,
                "{row['company']}" as company,
                "{row['title']}" as title,
                "{row['industry']}" as industry,
                "{row['status']}" as status,
                TIMESTAMP("{row['created_at']}") as created_at,
                TIMESTAMP("{row['updated_at']}") as updated_at
            ) AS source
            ON target.lead_id = source.lead_id
            WHEN MATCHED THEN
                UPDATE SET 
                    status = source.status,
                    updated_at = source.updated_at
            WHEN NOT MATCHED THEN
                INSERT (lead_id, first_name, last_name, email, company, title, industry, status, created_at, updated_at)
                VALUES (source.lead_id, source.first_name, source.last_name, source.email, source.company, source.title, source.industry, source.status, source.created_at, source.updated_at)
            """
            
            job = self.client.query(query)
            job.result()  # Wait for completion
            
            logging.info(f"Inserted/updated lead: {lead_data['email']}")
            return True
            
        except Exception as e:
            logging.error(f"Error inserting lead {lead_data.get('email', 'unknown')}: {e}")
            return False
    
    def insert_email_event(self, email: str, event_type: str, subject: str = None, campaign_id: str = None) -> bool:
        """Insert an email event."""
        if not self.client:
            return False
            
        try:
            table_id = f"{self.project_id}.{self.dataset_id}.email_events"
            
            event_id = f"{email}_{event_type}_{int(datetime.now().timestamp())}"
            
            row = {
                "event_id": event_id,
                "lead_email": email,
                "event_type": event_type,
                "email_subject": subject or "",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "campaign_id": campaign_id or "default",
            }
            
            errors = self.client.insert_rows_json(
                self.client.get_table(table_id), 
                [row]
            )
            
            if errors:
                logging.error(f"Error inserting email event: {errors}")
                return False
            
            logging.info(f"Inserted email event: {event_type} for {email}")
            return True
            
        except Exception as e:
            logging.error(f"Error inserting email event for {email}: {e}")
            return False
    
    def update_lead_status(self, email: str, status: str) -> bool:
        """Update lead status."""
        if not self.client:
            return False
            
        try:
            table_id = f"{self.project_id}.{self.dataset_id}.leads"
            lead_id = self._generate_lead_id(email)
            
            query = f"""
            UPDATE `{table_id}`
            SET status = "{status}", updated_at = CURRENT_TIMESTAMP()
            WHERE lead_id = "{lead_id}"
            """
            
            job = self.client.query(query)
            job.result()
            
            logging.info(f"Updated lead status for {email} to {status}")
            return True
            
        except Exception as e:
            logging.error(f"Error updating lead status for {email}: {e}")
            return False
    
    def get_campaign_analytics(self, campaign_id: str = "default") -> Dict[str, Any]:
        """Get campaign analytics."""
        if not self.client:
            return {}
            
        try:
            query = f"""
            SELECT 
                COUNT(DISTINCT l.lead_id) as total_leads,
                COUNT(CASE WHEN e.event_type = 'INITIAL_SENT' THEN 1 END) as initial_emails_sent,
                COUNT(CASE WHEN e.event_type = 'FOLLOW_UP_SENT' THEN 1 END) as follow_up_emails_sent,
                COUNT(CASE WHEN e.event_type = 'REPLIED' THEN 1 END) as replies_received,
                SAFE_DIVIDE(
                    COUNT(CASE WHEN e.event_type = 'REPLIED' THEN 1 END),
                    COUNT(CASE WHEN e.event_type = 'INITIAL_SENT' THEN 1 END)
                ) * 100 as response_rate_percent
            FROM `{self.project_id}.{self.dataset_id}.leads` l
            LEFT JOIN `{self.project_id}.{self.dataset_id}.email_events` e 
                ON l.email = e.lead_email 
                AND e.campaign_id = "{campaign_id}"
            """
            
            job = self.client.query(query)
            results = job.result()
            
            for row in results:
                return {
                    "total_leads": row.total_leads or 0,
                    "initial_emails_sent": row.initial_emails_sent or 0,
                    "follow_up_emails_sent": row.follow_up_emails_sent or 0,
                    "replies_received": row.replies_received or 0,
                    "response_rate_percent": round(row.response_rate_percent or 0, 2)
                }
            
            return {}
            
        except Exception as e:
            logging.error(f"Error getting campaign analytics: {e}")
            return {}
    
    def _generate_lead_id(self, email: str) -> str:
        """Generate a consistent lead ID from email."""
        import hashlib
        return hashlib.md5(email.lower().encode()).hexdigest()


# Global BigQuery client instance
bq_client = BigQueryClient()
