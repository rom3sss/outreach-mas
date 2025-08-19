# agents/lead_gen_agent.py


import os
from utils.google_api_clients import get_sheets_service


class LeadGenerationAgent:
    def __init__(self):
        self.sheets_service = get_sheets_service()
        self.spreadsheet_id = os.getenv('GOOGLE_SHEET_ID')
        # Assumes the data is in a sheet named 'Sheet1' and starts at A2
        self.range_name = 'Sheet1!A2:F' 


    def fetch_leads(self):
        """
        Fetches lead data from the configured Google Sheet.
        """
        try:
            sheet = self.sheets_service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                        range=self.range_name).execute()
            values = result.get('values', [])


            if not values:
                print("No data found in the sheet.")
                return []


            leads = []
            for row in values:
                # Ensure row has enough columns to avoid IndexError
                if len(row) >= 6:
                    lead = {
                        "firstName": row[0],
                        "lastName": row[1],
                        "email": row[2],
                        "company": row[3],
                        "title": row[4],
                        "industry": row[5]
                    }
                    leads.append(lead)
            
            print(f"Successfully fetched {len(leads)} leads.")
            return leads


        except Exception as e:
            print(f"An error occurred fetching leads: {e}")
            return []