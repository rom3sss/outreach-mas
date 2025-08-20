#!/usr/bin/env python3
"""
BigQuery Setup Helper
This script will help you enable BigQuery API and test the connection.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def check_bigquery_setup():
    """Check if BigQuery is properly set up."""
    print("🔧 BIGQUERY SETUP CHECKER")
    print("=" * 50)
    
    try:
        from config import config
        print(f"✅ Project ID: {config.bigquery_project_id}")
        print(f"✅ Dataset ID: {config.bigquery_dataset_id}")
        print(f"✅ Location: {config.bigquery_location}")
        
        # Test BigQuery connection
        from utils.bigquery_client import bq_client
        
        if bq_client.client:
            print("✅ BigQuery client initialized successfully")
            
            # Test dataset access
            try:
                dataset_ref = bq_client.client.dataset(bq_client.dataset_id)
                dataset = bq_client.client.get_dataset(dataset_ref)
                print(f"✅ Dataset '{bq_client.dataset_id}' is accessible")
                
                # List tables
                tables = list(bq_client.client.list_tables(dataset))
                if tables:
                    print(f"✅ Found {len(tables)} tables:")
                    for table in tables:
                        print(f"   - {table.table_id}")
                else:
                    print("ℹ️  No tables found (they will be created on first run)")
                    
            except Exception as e:
                print(f"⚠️  Dataset access issue: {e}")
                print("\n🔧 SETUP INSTRUCTIONS:")
                print("1. Go to https://console.cloud.google.com/")
                print(f"2. Select project: {config.bigquery_project_id}")
                print("3. Enable BigQuery API:")
                print("   - Go to APIs & Services > Library")
                print("   - Search for 'BigQuery API'")
                print("   - Click 'Enable'")
                print("4. Create service account (if not done):")
                print("   - Go to IAM & Admin > Service Accounts")
                print("   - Create new service account")
                print("   - Add roles: BigQuery Admin, BigQuery Data Editor")
                print("   - Download JSON key and replace credentials.json")
                
        else:
            print("❌ BigQuery client failed to initialize")
            print("Check your credentials.json file and project permissions")
            
    except Exception as e:
        print(f"❌ Setup check failed: {e}")


def create_service_account_instructions():
    """Print instructions for creating a proper service account."""
    print("\n" + "=" * 60)
    print("🔑 SERVICE ACCOUNT SETUP FOR BIGQUERY")
    print("=" * 60)
    print()
    print("Your current credentials.json is for OAuth (user authentication).")
    print("For BigQuery, you need a Service Account with proper permissions.")
    print()
    print("STEPS TO CREATE SERVICE ACCOUNT:")
    print("1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts")
    print("2. Select your project: gemini-integration-439017")
    print("3. Click 'CREATE SERVICE ACCOUNT'")
    print("4. Fill in details:")
    print("   - Name: outreach-system-sa")
    print("   - Description: Service account for outreach system")
    print("5. Click 'CREATE AND CONTINUE'")
    print("6. Add these roles:")
    print("   - BigQuery Admin")
    print("   - BigQuery Data Editor") 
    print("   - Storage Admin (if using Cloud Storage)")
    print("7. Click 'CONTINUE' then 'DONE'")
    print("8. Click on the created service account")
    print("9. Go to 'KEYS' tab")
    print("10. Click 'ADD KEY' > 'Create new key' > 'JSON'")
    print("11. Download the JSON file")
    print("12. Replace your current credentials.json with this file")
    print()
    print("ALTERNATIVE: Use your current OAuth credentials")
    print("If you want to use your current setup, make sure your Google account")
    print("has BigQuery permissions in the project.")


if __name__ == "__main__":
    check_bigquery_setup()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        create_service_account_instructions()
