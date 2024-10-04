import json
from datetime import datetime, timedelta
from logger import logger

def store_content(content, timestamp):
    logger.info(f"Storing content with timestamp: {timestamp}")
    try:
        with open('newsletter_content.json', 'a') as f:
            json.dump({'content': content, 'timestamp': timestamp}, f)
            f.write('\n')
        logger.info("Content successfully stored")
    except Exception as e:
        logger.error(f"Error occurred while storing content: {e}")
        raise

def get_weekly_content():
    logger.info("Retrieving weekly content")
    one_week_ago = datetime.now() - timedelta(days=7)
    weekly_content = []
    try:
        with open('newsletter_content.json', 'r') as f:
            for line in f:
                data = json.loads(line)
                if datetime.fromisoformat(data['timestamp']) > one_week_ago:
                    weekly_content.append(data['content'])
        logger.info(f"Retrieved {len(weekly_content)} content items from the past week")
        return ' '.join(weekly_content)
    except FileNotFoundError:
        logger.warning("newsletter_content.json file not found. Returning empty content.")
        return ''
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON in newsletter_content.json: {e}")
        return ''
    except Exception as e:
        logger.error(f"Unexpected error occurred while retrieving weekly content: {e}")
        return ''