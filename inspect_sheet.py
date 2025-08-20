#!/usr/bin/env python3
"""
Quick script to inspect your Google Sheet structure.
"""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from utils.google_api_clients import get_sheets_service

def inspect_sheet():
    print("🔍 Inspecting your Google Sheet...")
    print("=" * 50)
    
    sheets_service = get_sheets_service()
    if not sheets_service:
        print("❌ Could not connect to Sheets service")
        return
    
    try:
        # Get sheet metadata
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=config.google_sheet_id
        ).execute()
        
        print(f"📊 Sheet Title: {spreadsheet.get('properties', {}).get('title', 'Unknown')}")
        print(f"📋 Available Sheets:")
        
        sheets = spreadsheet.get('sheets', [])
        for i, sheet in enumerate(sheets):
            sheet_title = sheet.get('properties', {}).get('title', f'Sheet{i+1}')
            print(f"  {i+1}. {sheet_title}")
        
        # Try to read from the first sheet
        if sheets:
            first_sheet = sheets[0].get('properties', {}).get('title', 'Sheet1')
            print(f"\n📖 Trying to read from '{first_sheet}'...")
            
            # Read first 10 rows to see what's there
            range_name = f"{first_sheet}!A1:F10"
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=config.google_sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if values:
                print(f"✅ Found {len(values)} rows of data:")
                for i, row in enumerate(values[:5], 1):  # Show first 5 rows
                    print(f"  Row {i}: {row}")
                if len(values) > 5:
                    print(f"  ... and {len(values) - 5} more rows")
            else:
                print("⚠️  No data found in the sheet")
                print("💡 Make sure to add some test data with headers:")
                print("   Row 1: First Name | Last Name | Email | Company | Title | Industry")
                print("   Row 2: John | Doe | john@example.com | ACME Corp | CEO | Technology")
        
    except Exception as e:
        print(f"❌ Error inspecting sheet: {e}")

if __name__ == "__main__":
    inspect_sheet()
