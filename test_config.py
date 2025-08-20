#!/usr/bin/env python3
"""
Quick test script to validate Google API credentials and configuration.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import config
    from utils.google_api_clients import get_gmail_service, get_sheets_service
    
    print("🧪 Testing Google API Configuration...")
    print("=" * 50)
    
    # Test configuration
    print("📋 Configuration Check:")
    print(f"  ✅ Google API Key: {'✓ Present' if config.google_api_key else '❌ Missing'}")
    print(f"  ✅ Sheet ID: {'✓ Present' if config.google_sheet_id else '❌ Missing'}")
    print(f"  ✅ Sender Email: {'✓ Present' if config.sender_email else '❌ Missing'}")
    print(f"  ✅ Credentials File: {'✓ Present' if os.path.exists(config.google_credentials_path) else '❌ Missing'}")
    
    # Test Google Services
    print("\n🔌 API Connection Test:")
    
    # Test Gmail API
    print("  📧 Testing Gmail API...")
    gmail_service = get_gmail_service()
    if gmail_service:
        try:
            profile = gmail_service.users().getProfile(userId='me').execute()
            print(f"    ✅ Gmail API: Connected as {profile.get('emailAddress')}")
        except Exception as e:
            print(f"    ❌ Gmail API Error: {e}")
    else:
        print("    ❌ Gmail API: Failed to initialize")
    
    # Test Sheets API
    print("  📊 Testing Sheets API...")
    sheets_service = get_sheets_service()
    if sheets_service:
        try:
            # Try to access the configured sheet
            result = sheets_service.spreadsheets().get(
                spreadsheetId=config.google_sheet_id
            ).execute()
            print(f"    ✅ Sheets API: Connected to '{result.get('properties', {}).get('title', 'Unknown')}'")
        except Exception as e:
            print(f"    ⚠️  Sheets API: Service OK, but sheet access failed: {e}")
            print(f"      Check Sheet ID and sharing permissions")
    else:
        print("    ❌ Sheets API: Failed to initialize")
    
    print("\n" + "=" * 50)
    print("✅ Configuration test completed!")
    print("\n📋 If you see any ❌ errors above:")
    print("  1. Check your .env file values")
    print("  2. Verify credentials.json is in the project root")
    print("  3. Make sure APIs are enabled in Google Cloud Console")
    print("  4. Check Google Sheet sharing permissions")

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Run: python3 setup.py")
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
