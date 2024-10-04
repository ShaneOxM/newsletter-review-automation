# main.py
import schedule
import time
from datetime import datetime
from email_handler import connect_to_email, get_newsletter_emails, process_email
from insight_extractor import extract_insights
from ai_processor import process_newsletters
from content_processor import store_content, get_weekly_content
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, IMAP_SERVER, NEWSLETTER_LABEL
from logger import logger
from dotenv import load_dotenv
from report_handler import handle_report

# Load environment variables from .env file
load_dotenv()

def process_daily_newsletters():
    try:
        logger.info("Starting process_daily_newsletters function")
        logger.info("Connecting to email server...")
        mail = connect_to_email()
        logger.info("Successfully connected to email server")

        logger.info("Fetching newsletter emails...")
        email_ids = get_newsletter_emails(mail)
        logger.info(f"Found {len(email_ids)} newsletter emails")

        newsletters = []
        for i, email_id in enumerate(email_ids, 1):
            logger.info(f"Processing email {i} of {len(email_ids)}")
            email_data = process_email(mail, email_id)
            logger.info(f"Extracting insights for email {i}")
            insights = extract_insights(email_data)

            newsletters.append({
                'content': email_data['content'],
                'subject': email_data['subject'],
                'sender': email_data['sender'],
                'insights': insights
            })

            logger.info(f"Storing content for email {i}")
            store_content(email_data['content'], datetime.now().isoformat())

        mail.logout()
        logger.info("Logged out from email server")

        logger.info(f"Processed {len(newsletters)} newsletters")
        return newsletters
    except Exception as e:
        logger.error(f"Error in process_daily_newsletters: {e}")
        return []

def daily_job():
    logger.info("Starting daily newsletter processing job")
    newsletters = process_daily_newsletters()
    if newsletters:
        logger.info(f"Processing {len(newsletters)} newsletters")
        summary = process_newsletters(newsletters, output_type='file', output_name=f'daily_summary_{datetime.now().strftime("%Y%m%d")}')
        logger.info(f"Daily summary saved to: {summary}")
    else:
        logger.info("No newsletters processed today")
    logger.info("Daily newsletter processing job completed")

def weekly_report_job():
    try:
        logger.info("Starting weekly report generation")
        content = get_weekly_content()
        if content:
            logger.info("Processing weekly content")
            summary = process_newsletters([{'content': content}], output_type='string')
            logger.info("Handling weekly report")
            file_path, doc_id = handle_report(summary)
            logger.info(f"Weekly report saved to file: {file_path}")
            logger.info(f"Weekly report saved to Google Docs with ID: {doc_id}")
        else:
            logger.warning("No content found for the past week")
    except Exception as e:
        logger.error(f"Error in weekly_report_job: {e}")
    logger.info("Weekly report generation completed")

def main():
    logger.info("Newsletter Automation Started")
    
    schedule.every().day.at("09:00").do(daily_job)
    schedule.every().monday.at("10:00").do(weekly_report_job)

    logger.info("Running initial daily job")
    daily_job()  # Run immediately once

    logger.info("Entering main loop")
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    main()