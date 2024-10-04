import imaplib
import email
from datetime import datetime, timedelta
from email.header import decode_header
import base64
import os
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, IMAP_SERVER, NEWSLETTER_LABEL
from logger import logger

def connect_to_email():
    logger.info(f"Attempting to connect to email server: {IMAP_SERVER}")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        logger.info("Successfully connected and logged in to email server")
        return mail
    except imaplib.IMAP4.error as e:
        logger.error(f"IMAP error occurred while connecting to email server: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error occurred while connecting to email server: {e}")
        raise

def get_newsletter_emails(mail):
    logger.info(f"Searching for recent emails in folder: {NEWSLETTER_LABEL}")
    try:
        mail.select(NEWSLETTER_LABEL)
        date = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
        _, search_data = mail.search(None, f'(SINCE "{date}")')
        email_ids = search_data[0].split()
        logger.info(f"Found {len(email_ids)} recent emails in the newsletter folder")
        return email_ids
    except Exception as e:
        logger.error(f"Error occurred while fetching recent newsletter emails: {e}")
        raise

def process_email(mail, email_id):
    logger.info(f"Processing email with ID: {email_id}")
    try:
        _, msg_data = mail.fetch(email_id, "(RFC822)")
        email_body = msg_data[0][1]
        msg = email.message_from_bytes(email_body)
        
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")
        
        sender = msg.get("From")
        
        content = ""
        attachments = []
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    content += part.get_payload(decode=True).decode()
                elif content_type == "text/html":
                    # If no plain text is found, use HTML content
                    if not content:
                        content = part.get_payload(decode=True).decode()
                elif part.get_filename():
                    # Handle attachments
                    filename = part.get_filename()
                    attachment_data = part.get_payload(decode=True)
                    attachments.append((filename, attachment_data))
        else:
            content = msg.get_payload(decode=True).decode()
        
        logger.info(f"Successfully processed email: {subject}")
        return {
            "subject": subject,
            "sender": sender,
            "content": content,
            "attachments": attachments
        }
    except Exception as e:
        logger.error(f"Error occurred while processing email {email_id}: {e}")
        raise

def save_attachments(attachments, email_id):
    attachment_dir = "attachments"
    if not os.path.exists(attachment_dir):
        os.makedirs(attachment_dir)
    
    saved_paths = []
    for filename, data in attachments:
        safe_filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).rstrip()
        filepath = os.path.join(attachment_dir, f"{email_id}_{safe_filename}")
        with open(filepath, 'wb') as f:
            f.write(data)
        saved_paths.append(filepath)
    
    return saved_paths