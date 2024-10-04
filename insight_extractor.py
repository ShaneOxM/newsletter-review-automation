import re
from logger import logger

def extract_insights(email_data):
    logger.info(f"Extracting insights from email: {email_data['subject']}")
    insights = []
    
    # Extract URLs
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', email_data["content"])
    if urls:
        logger.info(f"Found {len(urls)} URLs in the email")
        insights.append(f"URLs found: {urls}")
    
    # Extract key phrases
    key_phrases = ["new release", "important update", "breaking news"]
    for phrase in key_phrases:
        if phrase in email_data["content"].lower():
            logger.info(f"Found key phrase: {phrase}")
            insights.append(f"Key phrase found: {phrase}")
    
    logger.info(f"Extracted {len(insights)} insights from the email")
    return insights