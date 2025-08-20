#!/usr/bin/env python3
"""
Setup script for the Multi-Agent Email Outreach System
Run this script to set up your environment and validate configuration.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)


def setup_environment():
    """Set up environment configuration."""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  .env file not found")
        print("Please copy the .env template and fill in your values:")
        print("  cp .env.template .env")
        print("  # Then edit .env with your actual values")


def create_directories():
    """Create necessary directories."""
    directories = ["logs", "database"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")


def validate_structure():
    """Validate the project structure."""
    required_files = [
        "main.py",
        "config.py",
        "agents/orchestrator.py",
        "agents/lead_gen_agent.py",
        "agents/email_crafting_agent.py",
        "agents/sending_agent.py",
        "agents/follow_up_agent.py",
        "utils/google_api_clients.py",
        "database/lead_status.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        sys.exit(1)
    
    print("✅ All required files present")


def main():
    """Main setup function."""
    print("🚀 Setting up Multi-Agent Email Outreach System")
    print("=" * 50)
    
    check_python_version()
    validate_structure()
    create_directories()
    install_dependencies()
    setup_environment()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Get your Google API credentials (credentials.json)")
    print("2. Fill in your .env file with actual values")
    print("3. Run: python main.py")


if __name__ == "__main__":
    main()
