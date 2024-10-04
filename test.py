from email_handler import connect_to_email, get_newsletter_emails, process_email
from insight_extractor import extract_insights
from ai_processor import generate_embeddings, generate_summary
from content_processor import store_content, get_weekly_content
from report_handler import handle_report
from logger import logger

def test_email_processing():
    logger.info("Testing email processing")
    mail = connect_to_email()
    email_ids = get_newsletter_emails(mail)
    if email_ids:
        email_data = process_email(mail, email_ids[0])
        insights = extract_insights(email_data)
        logger.info(f"Processed email: {email_data['subject']}")
        logger.info(f"Insights: {insights}")
    else:
        logger.warning("No emails found for testing")
    mail.logout()

def test_weekly_report():
    logger.info("Testing weekly report generation")
    content = get_weekly_content()
    if content:
        embeddings = generate_embeddings(content)
        summary = generate_summary(embeddings)
        handle_report(summary)
    else:
        logger.warning("No content found for testing weekly report")

if __name__ == "__main__":
    test_email_processing()
    test_weekly_report()