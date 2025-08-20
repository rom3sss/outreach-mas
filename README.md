# Multi-Agent Email Outreach System

A Python-based multi-agent system designed to automate personalized cold email outreach. The system sources leads from Google Sheets, uses Google's Gemini LLM for personalization, sends initial emails, and manages intelligent follow-ups.

## 🌟 Features

- **Automated Lead Sourcing**: Fetches lead data directly from Google Sheets with validation
- **LLM-Powered Personalization**: Uses Google Gemini for natural follow-up messages
- **Stateful Lead Management**: Tracks lead status with comprehensive logging
- **Intelligent Follow-up Logic**: Checks for replies and sends follow-ups after configurable delays
- **Modular Architecture**: Five specialized agents orchestrated by a central coordinator
- **Robust Error Handling**: Comprehensive logging and graceful error recovery
- **Type Safety**: Full type hints for better code maintainability

## 🏗️ System Architecture

The system uses a multi-agent architecture with the following components:

- **OrchestratorAgent**: Central coordinator managing workflow and state
- **LeadGenerationAgent**: Fetches and validates leads from Google Sheets
- **EmailCraftingAgent**: Creates personalized emails using templates and LLM
- **SendingAgent**: Handles email delivery via Gmail API
- **FollowUpAgent**: Manages reply detection and follow-up timing

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Google account with Gmail and Google Sheets access
- Google Cloud Project with APIs enabled

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd outreach-mas

# Run the setup script
python setup.py

# Or manually install dependencies
pip install -r requirements.txt
```

### 3. Configuration

1. **Set up Google Cloud credentials**:
   - Download `credentials.json` from your Google Cloud Console
   - Place it in the project root directory

2. **Configure environment variables**:
   ```bash
   # Copy the template and edit with your values
   cp .env.template .env
   # Edit .env with your actual configuration
   ```

3. **Prepare your Google Sheet**:
   - Create a sheet with columns: First Name, Last Name, Email, Company, Title, Industry
   - Share the sheet with your service account email

### 4. Run the System

```bash
python main.py
```

## 📁 Project Structure

```
outreach-mas/
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py          # Central coordinator
│   ├── lead_gen_agent.py        # Lead sourcing and validation
│   ├── email_crafting_agent.py  # Email creation with LLM
│   ├── sending_agent.py         # Email delivery
│   └── follow_up_agent.py       # Reply detection and timing
├── utils/
│   ├── __init__.py
│   └── google_api_clients.py    # Google API utilities
├── database/
│   └── lead_status.json         # Lead state persistence
├── logs/                        # Application logs
├── main.py                      # Application entry point
├── config.py                    # Configuration management
├── setup.py                     # Setup and validation script
├── requirements.txt             # Dependencies
├── .env                         # Environment variables
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

Create a Google Cloud Project: Go to the Google Cloud Console and create a new project.

Enable APIs: In your project, enable the Google Sheets API and the Gmail API.

Configure OAuth Consent Screen:

Navigate to APIs & Services > OAuth consent screen.

Select External and fill in the required application details.

Create Credentials:

Navigate to APIs & Services > Credentials.

Click + CREATE CREDENTIALS and select OAuth client ID.

For "Application type", choose Desktop app.

After creation, click DOWNLOAD JSON.

Rename the downloaded file to credentials.json and place it in the root directory of your project.

### 4. Configure Environment Variables
Create a file named .env in the root of your project.

Copy the contents below into the file and fill in your actual values.

Ini, TOML

# .env

# LLM Configuration (Google Gemini)
GOOGLE_API_KEY="your_google_gemini_api_key_here"

# Google API Configuration
GOOGLE_SHEET_ID="your_google_sheet_id_here"
GOOGLE_CREDENTIALS_PATH="credentials.json" 

# Email Configuration
SENDER_EMAIL="your.email@gmail.com"
YOUR_NAME="[Your Name]"
YOUR_TITLE="[Your Title]"
PORTFOLIO_LINK="[Link to Portfolio/Showreel]"

# Follow-up Logic
FOLLOW_UP_DELAY_HOURS=48
### 5. Prepare Your Google Sheet
Create a new Google Sheet.

Get the Sheet ID from its URL: .../spreadsheets/d/THIS_IS_THE_ID/edit... and add it to your .env file.

Name the sheet tab Sheet1.

Set up the following columns in this exact order in the first row:

FirstName

LastName

EmailAddress

CompanyName

JobTitle

Industry

Add your lead data starting from the second row.

## How to Run the System
First Run (Authentication):
Open a terminal in the project's root directory and run the main script:

Bash

python main.py
Your web browser will open and ask you to authorize the application. Grant it permission to access your Gmail and Sheets. After you approve, token_*.pickle files will be created in your directory to store your credentials for future runs.

Subsequent Runs:
Simply run the script again. It will use the saved tokens and will not require you to log in again.

Bash

python main.py
The orchestrator will log its actions to the console, showing you which leads are being processed, sent, or skipped. The database/lead_status.json file will be updated in real-time.
