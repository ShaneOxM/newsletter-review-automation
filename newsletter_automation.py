import schedule
import time
from datetime import datetime, timedelta
import json
import os
from email_handler import connect_to_email, get_newsletter_emails, process_email
from insight_extractor import extract_insights
from ai_processor import generate_summary
from report_handler import generate_report, send_email_report
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, IMAP_SERVER, NEWSLETTER_LABEL
from logger import logger

def load_processed_newsletters():
    try:
        with open('processed_newsletters.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_processed_newsletters(processed):
    with open('processed_newsletters.json', 'w') as f:
        json.dump(processed, f)

def is_newsletter_processed(email_id, processed_newsletters):
    return email_id in processed_newsletters

def mark_newsletter_processed(email_id, processed_newsletters):
    processed_newsletters[email_id] = datetime.now().isoformat()
    save_processed_newsletters(processed_newsletters)

def check_for_new_newsletters():
    logger.info("Checking for new newsletters...")
    mail = connect_to_email()
    email_ids = get_newsletter_emails(mail)
    
    processed_newsletters = load_processed_newsletters()
    new_newsletters = [email_id for email_id in email_ids if not is_newsletter_processed(email_id, processed_newsletters)]
    
    for email_id in new_newsletters:
        email_data = process_email(mail, email_id)
        insights = extract_insights(email_data)
        summary = generate_summary(insights)
        report = generate_report(summary)
        send_email_report(report)
        mark_newsletter_processed(email_id, processed_newsletters)
    
    mail.logout()
    logger.info(f"Processed {len(new_newsletters)} new newsletters")

def run_newsletter_check():
    schedule.every(3).days.do(check_for_new_newsletters)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    logger.info("Starting newsletter automation script")
    run_newsletter_check()