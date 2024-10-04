import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email Configuration
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
IMAP_SERVER = os.getenv('IMAP_SERVER')
NEWSLETTER_LABEL = os.getenv('NEWSLETTER_LABEL')

# Report Configuration
REPORT_RECIPIENT = os.getenv('REPORT_RECIPIENT')

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Scheduling Configuration
DAILY_PROCESS_TIME = os.getenv('DAILY_PROCESS_TIME')
WEEKLY_REPORT_TIME = os.getenv('WEEKLY_REPORT_TIME')
WEEKLY_REPORT_DAY = os.getenv('WEEKLY_REPORT_DAY')

# Print out the values for debugging
print(f"EMAIL_ADDRESS: {EMAIL_ADDRESS}")
print(f"IMAP_SERVER: {IMAP_SERVER}")
print(f"NEWSLETTER_LABEL: {NEWSLETTER_LABEL}")
print(f"REPORT_RECIPIENT: {REPORT_RECIPIENT}")
print(f"OPENAI_API_KEY: {'*' * len(OPENAI_API_KEY) if OPENAI_API_KEY else 'Not set'}")

# Check if all required variables are set
if not all([EMAIL_ADDRESS, EMAIL_PASSWORD, IMAP_SERVER, NEWSLETTER_LABEL, REPORT_RECIPIENT, OPENAI_API_KEY]):
    raise ValueError("Missing required environment variables. Please check your .env file.")