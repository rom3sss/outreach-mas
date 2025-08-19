## Multi-Agent Email Outreach System
This project is a Python-based multi-agent system designed to automate personalized cold email outreach. It sources leads from a Google Sheet, uses Google's Gemini LLM to personalize emails, sends an initial email, and manages a single follow-up if no reply is received within a specified timeframe.

## Features
Automated Lead Sourcing: Fetches lead data directly from a Google Sheet.

LLM-Powered Personalization: Uses Google Gemini to craft natural and relevant follow-up messages.

Stateful Lead Management: Tracks the status of each lead (PENDING, INITIAL_EMAIL_SENT, REPLIED, etc.) in a simple JSON database.

Automated Follow-up Logic: Intelligently checks for replies via the Gmail API and sends a follow-up email after a configurable delay (e.g., 48 hours).

Modular Architecture: Built with five distinct agents, each with a specific role, orchestrated by a central coordinator.

Secure Configuration: Manages all sensitive keys and settings through a .env file.

## System Architecture
The system operates on a multi-agent model where a central OrchestratorAgent coordinates the workflow between specialized agents:

OrchestratorAgent: The brain of the operation. Manages the overall workflow, state, and data flow between other agents.

LeadGenerationAgent: Connects to Google Sheets to source and structure lead information.

EmailCraftingAgent: Uses the Gemini LLM to draft personalized follow-up emails.

SendingAgent: Dispatches emails using the Gmail API.

FollowUpAgent: Monitors for replies and determines when a follow-up should be sent.

## Setup and Installation
Follow these steps to get the system up and running.

### 1. Prerequisites
Python 3.10 or higher.

A Google account with Gmail and Google Drive (for Sheets) enabled.

### 2. Project Setup
Clone or Download: Get the code and place it in a local directory.

File Structure: Ensure your project has the required file structure, including the agents/, database/, and utils/ directories.

Install Dependencies: Open your terminal in the project root and run:

Bash

pip install -r requirements.txt
### 3. Google Cloud Authentication
This is the most critical setup step. This process allows the script to securely access your Google account.

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
