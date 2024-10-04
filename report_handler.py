import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, REPORT_RECIPIENT
from logger import logger
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def create_report_directory():
    base_dir = "weekly_reports"
    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")
    week = datetime.now().strftime("%V")
    
    report_dir = os.path.join(base_dir, year, month, f"Week_{week}")
    os.makedirs(report_dir, exist_ok=True)
    
    return report_dir

def save_report_to_file(summary):
    report_dir = create_report_directory()
    
    filename = f"weekly_report_{datetime.now().strftime('%Y%m%d')}.txt"
    filepath = os.path.join(report_dir, filename)
    
    with open(filepath, 'w') as f:
        f.write(summary)
    
    logger.info(f"Report saved to {filepath}")
    return filepath

def send_email_report(summary):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = REPORT_RECIPIENT
    msg['Subject'] = f"Weekly Newsletter Summary - {datetime.now().strftime('%Y-%m-%d')}"

    msg.attach(MIMEText(summary, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        logger.info("Email report sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email report: {e}")

def format_google_docs_report(service, document_id, content):
    requests = [
        {
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        },
        {
            'updateParagraphStyle': {
                'range': {'startIndex': 1, 'endIndex': len(content) + 1},
                'paragraphStyle': {
                    'namedStyleType': 'NORMAL_TEXT',
                    'lineSpacing': 115,
                },
                'fields': 'namedStyleType,lineSpacing'
            }
        },
        {
            'updateTextStyle': {
                'range': {'startIndex': 1, 'endIndex': content.index('\n')},
                'textStyle': {'bold': True, 'fontSize': {'magnitude': 18, 'unit': 'PT'}},
                'fields': 'bold,fontSize'
            }
        }
    ]
    
    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

def save_to_google_docs(summary, title):
    logger.info("Saving summary to Google Docs")
    try:
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/documents'])
        service = build('docs', 'v1', credentials=creds)
        
        document = service.documents().create(body={'title': title}).execute()
        document_id = document['documentId']
        
        format_google_docs_report(service, document_id, summary)
        
        logger.info(f"Summary saved to Google Docs with ID: {document_id}")
        return document_id
    except Exception as e:
        logger.error(f"Error saving to Google Docs: {e}")
        raise

def handle_report(summary):
    logger.info("Handling weekly report")
    file_path = save_report_to_file(summary)
    send_email_report(summary)
    doc_id = save_to_google_docs(summary, f"Weekly Newsletter Summary - {datetime.now().strftime('%Y-%m-%d')}")
    logger.info(f"Weekly report saved to file: {file_path}")
    logger.info(f"Weekly report saved to Google Docs with ID: {doc_id}")
    logger.info("Weekly report handling completed")
    return file_path, doc_id