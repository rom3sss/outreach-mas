"""Orchestrator Agent - Central coordinator for the multi-agent outreach system."""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from agents.lead_gen_agent import LeadGenerationAgent
from agents.email_crafting_agent import EmailCraftingAgent
from agents.sending_agent import SendingAgent
from agents.follow_up_agent import FollowUpAgent
from utils.bigquery_client import bq_client


class OrchestratorAgent:
    """Central orchestrator that coordinates workflow between specialized agents."""
    
    def __init__(self, state_file: str = 'database/lead_status.json'):
        """
        Initialize the Orchestrator Agent.
        
        Args:
            state_file: Path to the JSON file for persisting lead status
        """
        self.state_file = state_file
        self.lead_status = self._load_state()

        # Initialize all subordinate agents
        logging.info("Initializing subordinate agents...")
        self.lead_gen_agent = LeadGenerationAgent()
        self.email_crafting_agent = EmailCraftingAgent()
        self.sending_agent = SendingAgent()
        self.follow_up_agent = FollowUpAgent()
        logging.info("All agents initialized successfully")

    def _load_state(self) -> Dict[str, Any]:
        """
        Load the current state from the JSON file.
        
        Returns:
            Dictionary containing lead status data
        """
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                logging.info(f"Loaded state for {len(state)} leads")
                return state
        except FileNotFoundError:
            logging.info("No existing state file found, starting fresh")
            return {}
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in state file: {e}")
            return {}
        except Exception as e:
            logging.error(f"Error loading state: {e}")
            return {}

    def _save_state(self) -> None:
        """Save the current state to the JSON file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.lead_status, f, indent=4, default=str)
            logging.debug("State saved successfully")
        except Exception as e:
            logging.error(f"Error saving state: {e}")

    def _update_lead_status(self, email: str, status: str, timestamp: str = None) -> None:
        """
        Update the status for a given lead and save the state.
        
        Args:
            email: Lead email address
            status: New status to set
            timestamp: Optional timestamp for the status change
        """
        if email not in self.lead_status:
            self.lead_status[email] = {}
        
        self.lead_status[email]['status'] = status
        
        # Add specific timestamps based on status
        if status == 'INITIAL_EMAIL_SENT':
            self.lead_status[email]['initial_sent_timestamp'] = timestamp
        elif status == 'FOLLOW_UP_SENT':
            self.lead_status[email]['follow_up_sent_timestamp'] = timestamp
        elif status == 'REPLIED':
            self.lead_status[email]['replied_timestamp'] = timestamp
            
        self._save_state()
        
        # Update BigQuery
        if bq_client.client:
            bq_client.update_lead_status(email, status)
            
            # Insert email event
            if status == 'INITIAL_EMAIL_SENT':
                bq_client.insert_email_event(email, 'INITIAL_SENT')
            elif status == 'FOLLOW_UP_SENT':
                bq_client.insert_email_event(email, 'FOLLOW_UP_SENT')
            elif status == 'REPLIED':
                bq_client.insert_email_event(email, 'REPLIED')
        
        logging.info(f"Updated status for {email} to {status}")

    def _process_new_leads(self, all_leads: List[Dict[str, str]]) -> None:
        """
        Process initial outreach for new leads.
        
        Args:
            all_leads: List of all lead data
        """
        new_leads_count = 0
        
        for lead in all_leads:
            email = lead['email']
            status = self.lead_status.get(email, {}).get('status', 'PENDING')

            if status == 'PENDING':
                logging.info(f"Processing new lead: {email}")
                new_leads_count += 1
                
                # Draft email
                draft = self.email_crafting_agent.draft_initial_email(lead)
                
                if draft and draft.get('subject') and draft.get('body'):
                    # Send email
                    success = self.sending_agent.send_email(
                        email, draft['subject'], draft['body']
                    )
                    
                    # Update status
                    if success:
                        sent_timestamp = datetime.now(timezone.utc).isoformat()
                        self._update_lead_status(email, 'INITIAL_EMAIL_SENT', timestamp=sent_timestamp)
                    else:
                        logging.error(f"Failed to send initial email to {email}")
                else:
                    logging.error(f"Failed to draft initial email for {email}")
            else:
                logging.debug(f"Skipping lead {email} with status: {status}")
        
        logging.info(f"Processed {new_leads_count} new leads for initial outreach")

    def _process_follow_ups(self, all_leads: List[Dict[str, str]]) -> None:
        """
        Process follow-ups and check for replies.
        
        Args:
            all_leads: List of all lead data
        """
        follow_up_count = 0
        reply_count = 0
        
        for email, data in list(self.lead_status.items()):
            if data.get('status') != 'INITIAL_EMAIL_SENT':
                continue
                
            logging.debug(f"Checking status for {email}")
            
            # Check for reply
            initial_sent_time = data.get('initial_sent_timestamp')
            if not initial_sent_time:
                logging.warning(f"Missing initial_sent_timestamp for {email}")
                continue
                
            if self.follow_up_agent.check_for_reply(email, initial_sent_time):
                self._update_lead_status(
                    email, 'REPLIED', 
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
                reply_count += 1
                continue  # Stop processing this lead
            
            # Check if it's time to send a follow-up
            if self.follow_up_agent.should_send_follow_up(initial_sent_time):
                logging.info(f"Time to send follow-up to {email}")
                
                # Find the full lead data
                lead_data = next((l for l in all_leads if l['email'] == email), None)
                if not lead_data:
                    logging.error(f"Could not find lead data for {email} to send follow-up")
                    continue
                    
                # Draft and send follow-up
                follow_up_draft = self.email_crafting_agent.draft_follow_up_email(lead_data)
                if follow_up_draft and follow_up_draft.get('subject') and follow_up_draft.get('body'):
                    success = self.sending_agent.send_email(
                        email, follow_up_draft['subject'], follow_up_draft['body']
                    )
                    if success:
                        self._update_lead_status(
                            email, 'FOLLOW_UP_SENT',
                            timestamp=datetime.now(timezone.utc).isoformat()
                        )
                        follow_up_count += 1
                    else:
                        logging.error(f"Failed to send follow-up to {email}")
                else:
                    logging.error(f"Failed to draft follow-up for {email}")
        
        logging.info(f"Processed follow-ups: {follow_up_count} sent, {reply_count} replies detected")

    def run_workflow(self) -> None:
        """Main execution loop for the outreach workflow."""
        logging.info("=" * 50)
        logging.info("Starting outreach workflow...")
        logging.info("=" * 50)

        try:
            # 1. Fetch leads
            all_leads = self.lead_gen_agent.fetch_leads()
            if not all_leads:
                logging.warning("No leads fetched. Exiting workflow")
                return

            # Store leads in BigQuery
            if bq_client.client:
                for lead in all_leads:
                    lead_with_status = lead.copy()
                    lead_with_status['status'] = self.lead_status.get(lead['email'], {}).get('status', 'PENDING')
                    bq_client.insert_lead(lead_with_status)

            # 2. Process Initial Outreach for new leads
            logging.info("Processing initial outreach for new leads...")
            self._process_new_leads(all_leads)
            
            # 3. Process Follow-ups and check for replies
            logging.info("Processing follow-ups and checking for replies...")
            self._process_follow_ups(all_leads)
            
            # 4. Generate and log analytics
            if bq_client.client:
                analytics = bq_client.get_campaign_analytics()
                logging.info("="*50)
                logging.info("CAMPAIGN ANALYTICS")
                logging.info("="*50)
                logging.info(f"Total Leads: {analytics.get('total_leads', 0)}")
                logging.info(f"Initial Emails Sent: {analytics.get('initial_emails_sent', 0)}")
                logging.info(f"Follow-up Emails Sent: {analytics.get('follow_up_emails_sent', 0)}")
                logging.info(f"Replies Received: {analytics.get('replies_received', 0)}")
                logging.info(f"Response Rate: {analytics.get('response_rate_percent', 0):.2f}%")
                logging.info("="*50)
            
            logging.info("Workflow completed successfully")
            
        except Exception as e:
            logging.error(f"Workflow failed with error: {e}")
            raise
        finally:
            # Always save final state
            self._save_state()
