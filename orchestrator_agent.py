# agents/orchestrator.py


import json
import logging
from datetime import datetime, timezone


from agents.lead_gen_agent import LeadGenerationAgent
from agents.email_crafting_agent import EmailCraftingAgent
from agents.sending_agent import SendingAgent
from agents.follow_up_agent import FollowUpAgent


# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class OrchestratorAgent:
    def __init__(self, state_file='database/lead_status.json'):
        self.state_file = state_file
        self.lead_status = self._load_state()


        # Initialize all subordinate agents
        self.lead_gen_agent = LeadGenerationAgent()
        self.email_crafting_agent = EmailCraftingAgent()
        self.sending_agent = SendingAgent()
        self.follow_up_agent = FollowUpAgent()


    def _load_state(self):
        """Loads the current state from the JSON file."""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}


    def _save_state(self):
        """Saves the current state to the JSON file."""
        with open(self.state_file, 'w') as f:
            json.dump(self.lead_status, f, indent=4)


    def _update_lead_status(self, email: str, status: str, timestamp: str = None):
        """Updates the status for a given lead and saves the state."""
        if email not in self.lead_status:
            self.lead_status[email] = {}
        
        self.lead_status[email]['status'] = status
        if status == 'INITIAL_EMAIL_SENT':
            self.lead_status[email]['initial_sent_timestamp'] = timestamp
        elif status == 'FOLLOW_UP_SENT':
            self.lead_status[email]['follow_up_sent_timestamp'] = timestamp
        elif status == 'REPLIED':
            self.lead_status[email]['replied_timestamp'] = timestamp
            
        self._save_state()
        logging.info(f"Updated status for {email} to {status}.")


    def run_workflow(self):
        """Main execution loop for the outreach workflow."""
        logging.info("Starting outreach workflow...")


        # 1. Fetch leads
        all_leads = self.lead_gen_agent.fetch_leads()
        if not all_leads:
            logging.warning("No leads fetched. Exiting workflow.")
            return


        # 2. Process Initial Outreach for new leads
        for lead in all_leads:
            email = lead['email']
            status = self.lead_status.get(email, {}).get('status', 'PENDING')


            if status == 'PENDING':
                logging.info(f"Processing new lead: {email}")
                
                # Draft email
                draft = self.email_crafting_agent.draft_initial_email(lead)
                
                # Send email
                success = self.sending_agent.send_email(email, draft['subject'], draft['body'])
                
                # Update status
                if success:
                    sent_timestamp = datetime.now(timezone.utc).isoformat()
                    self._update_lead_status(email, 'INITIAL_EMAIL_SENT', timestamp=sent_timestamp)
            else:
                logging.info(f"Skipping lead {email} with status: {status}")
        
        logging.info("Initial outreach processing complete. Starting follow-up checks.")


        # 3. Process Follow-ups and check for replies
        for email, data in list(self.lead_status.items()):
            if data['status'] == 'INITIAL_EMAIL_SENT':
                logging.info(f"Checking status for {email}")
                
                # Check for reply
                initial_sent_time = data['initial_sent_timestamp']
                if self.follow_up_agent.check_for_reply(email, initial_sent_time):
                    self._update_lead_status(email, 'REPLIED', timestamp=datetime.now(timezone.utc).isoformat())
                    continue # Stop processing this lead
                
                # Check if it's time to send a follow-up
                if self.follow_up_agent.should_send_follow_up(initial_sent_time):
                    logging.info(f"Time to send follow-up to {email}")
                    
                    # Find the full lead data
                    lead_data = next((l for l in all_leads if l['email'] == email), None)
                    if not lead_data:
                        logging.error(f"Could not find lead data for {email} to send follow-up.")
                        continue
                        
                    # Draft and send follow-up
                    follow_up_draft = self.email_crafting_agent.draft_follow_up_email(lead_data)
                    if follow_up_draft:
                        success = self.sending_agent.send_email(email, follow_up_draft['subject'], follow_up_draft['body'])
                        if success:
                            self._update_lead_status(email, 'FOLLOW_UP_SENT', timestamp=datetime.now(timezone.utc).isoformat())
        
        logging.info("Workflow finished.")