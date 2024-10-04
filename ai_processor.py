from openai import OpenAI
from config import OPENAI_API_KEY
from logger import logger
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import hashlib
import json
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# Initialize the OpenAI client with the API key from config
client = OpenAI(api_key=OPENAI_API_KEY)

# Cache for embeddings
embedding_cache = {}

def truncate_text(text, max_tokens=1000):
    """Truncate text to a maximum number of tokens (approximate)."""
    words = text.split()
    return ' '.join(words[:max_tokens])

def get_cached_embedding(text):
    """Get embedding from cache or generate new one."""
    text_hash = hashlib.md5(text.encode()).hexdigest()
    if text_hash in embedding_cache:
        return embedding_cache[text_hash]
    return None

def save_cached_embedding(text, embedding):
    """Save embedding to cache."""
    text_hash = hashlib.md5(text.encode()).hexdigest()
    embedding_cache[text_hash] = embedding
    # Optionally save cache to disk to persist between runs
    with open('embedding_cache.json', 'w') as f:
        json.dump(embedding_cache, f)

def generate_embeddings(text):
    logger.info("Generating embeddings for text")
    try:
        cached_embedding = get_cached_embedding(text)
        if cached_embedding:
            logger.info("Using cached embedding")
            return cached_embedding

        truncated_text = truncate_text(text)
        response = client.embeddings.create(
            input=truncated_text,
            model="text-embedding-ada-002"
        )
        embedding = response.data[0].embedding
        save_cached_embedding(text, embedding)
        logger.info("Embeddings generated successfully")
        return embedding
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise

def generate_summary(content):
    logger.info("Generating detailed summary from content")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant that creates detailed, structured summaries of newsletter content. Your summaries should be engaging, insightful, and highlight the most important information."},
                {"role": "user", "content": f"""Please provide a comprehensive summary of the following newsletter content. 
                Include the following sections:
                1. Newsletter Name and Date
                2. Executive Summary (2-3 sentences)
                3. Main Topics Covered (bullet points)
                4. Key Insights (3-5 bullet points)
                5. Important Links or Resources
                6. Notable Quotes or Statistics
                7. Emerging Trends or Patterns
                8. Action Items or Takeaways
                9. Brief Analysis or Commentary

                Here's the content to summarize:

                {content[:4000]}"""}  # Increased character limit to 4000
            ],
            max_tokens=1500,  # Increased token limit
            n=1,
            temperature=0.7,
        )
        summary = response.choices[0].message.content.strip()
        logger.info("Detailed summary generated successfully")
        return summary
    except Exception as e:
        logger.error(f"Error generating detailed summary: {e}")
        raise

def analyze_sentiment(content):
    logger.info("Analyzing sentiment of content")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant that analyzes the sentiment of text."},
                {"role": "user", "content": f"Analyze the sentiment of the following text and provide a score from -1 (very negative) to 1 (very positive), along with a brief explanation:\n\n{content[:1000]}"}
            ],
            max_tokens=100,
            n=1,
            temperature=0.5,
        )
        sentiment_analysis = response.choices[0].message.content.strip()
        logger.info("Sentiment analysis completed successfully")
        return sentiment_analysis
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise

def generate_word_cloud(text):
    logger.info("Generating word cloud")
    try:
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig('wordcloud.png')
        logger.info("Word cloud generated successfully")
    except Exception as e:
        logger.error(f"Error generating word cloud: {e}")

def extract_topics(content):
    logger.info("Extracting main topics from content")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant that extracts main topics from text."},
                {"role": "user", "content": f"Extract the 5 main topics from the following text, providing a brief description for each:\n\n{content[:2000]}"}
            ],
            max_tokens=300,
            n=1,
            temperature=0.5,
        )
        topics = response.choices[0].message.content.strip()
        logger.info("Main topics extracted successfully")
        return topics
    except Exception as e:
        logger.error(f"Error extracting topics: {e}")
        raise

def extract_topics_lda(content, num_topics=5):
    logger.info("Extracting topics using LDA")
    try:
        # Split the content into sentences or paragraphs to create multiple documents
        documents = content.split('\n')
        
        # Ensure we have at least 2 documents
        if len(documents) < 2:
            documents = content.split('. ')
        
        if len(documents) < 2:
            logger.warning("Not enough content for LDA. Falling back to simple keyword extraction.")
            return extract_simple_topics(content)

        vectorizer = TfidfVectorizer(max_df=0.95, min_df=1, stop_words='english')
        doc_term_matrix = vectorizer.fit_transform(documents)
        
        lda = LatentDirichletAllocation(n_components=min(num_topics, len(documents)), random_state=42)
        lda.fit(doc_term_matrix)
        
        feature_names = vectorizer.get_feature_names_out()
        topics = []
        for topic_idx, topic in enumerate(lda.components_):
            top_words = [feature_names[i] for i in topic.argsort()[:-10 - 1:-1]]
            topics.append(f"Topic {topic_idx + 1}: {', '.join(top_words)}")
        
        logger.info("LDA topic extraction completed successfully")
        return topics
    except Exception as e:
        logger.error(f"Error extracting topics using LDA: {e}")
        logger.info("Falling back to simple keyword extraction")
        return extract_simple_topics(content)

def extract_simple_topics(content):
    logger.info("Extracting simple topics")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant that extracts main topics from text."},
                {"role": "user", "content": f"Extract the 5 main topics from the following text, providing a brief description for each:\n\n{content[:2000]}"}
            ],
            max_tokens=300,
            n=1,
            temperature=0.5,
        )
        topics = response.choices[0].message.content.strip()
        logger.info("Simple topic extraction completed successfully")
        return topics
    except Exception as e:
        logger.error(f"Error extracting simple topics: {e}")
        return "Unable to extract topics"

def analyze_newsletters(newsletters):
    logger.info("Analyzing newsletters")
    try:
        summaries = []
        sentiments = []
        all_content = ""
        topics = []

        for i, newsletter in enumerate(newsletters, 1):
            logger.info(f"Generating summary for newsletter {i} of {len(newsletters)}")
            summary = generate_summary(newsletter['content'])
            summaries.append(summary)
            
            sentiment = analyze_sentiment(newsletter['content'])
            sentiments.append(sentiment)
            
            all_content += newsletter['content'] + " "
            
            topic = extract_topics(newsletter['content'])
            topics.append(topic)

        lda_topics = extract_topics_lda(all_content)
        
        # Add LDA topics to the combined report
        combined_report = "Weekly Newsletter Report\n\n"
        combined_report += "=" * 50 + "\n\n"
        for i, (summary, sentiment, topic) in enumerate(zip(summaries, sentiments, topics), 1):
            combined_report += f"Newsletter {i}:\n\n"
            combined_report += summary + "\n\n"
            combined_report += f"Sentiment Analysis:\n{sentiment}\n\n"
            combined_report += f"Main Topics:\n{topic}\n\n"
            combined_report += "-" * 30 + "\n\n"
        
        combined_report += "LDA Topic Analysis:\n"
        for topic in lda_topics:
            combined_report += f"{topic}\n"
        combined_report += "\n"
        
        combined_report += "Word Cloud: See attached image 'wordcloud.png'\n\n"
        combined_report += "=" * 50 + "\n\n"
        combined_report += "End of Weekly Report"
        
        return combined_report
    except Exception as e:
        logger.error(f"Error analyzing newsletters: {e}")
        raise

def get_google_docs_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/documents'])
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', ['https://www.googleapis.com/auth/documents'])
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def save_to_google_docs(summary, title):
    logger.info("Saving summary to Google Docs")
    try:
        creds = get_google_docs_credentials()
        service = build('docs', 'v1', credentials=creds)
        
        document = service.documents().create(body={'title': title}).execute()
        doc_id = document['documentId']
        
        requests = [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': summary
                }
            }
        ]
        
        service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
        
        logger.info(f"Summary saved to Google Docs with ID: {doc_id}")
        return doc_id
    except HttpError as e:
        logger.error(f"Error saving to Google Docs: {e}")
        raise

def save_to_file(summary, filename):
    logger.info(f"Saving summary to file: {filename}")
    try:
        with open(filename, 'w') as f:
            f.write(summary)
        logger.info(f"Summary saved to file: {filename}")
    except Exception as e:
        logger.error(f"Error saving to file: {e}")
        raise

def process_newsletters(newsletters, output_type='file', output_name='newsletter_summary'):
    summary = analyze_newsletters(newsletters)
    
    if output_type == 'google_docs':
        return save_to_google_docs(summary, output_name)
    elif output_type == 'file':
        filename = f"{output_name}.txt"
        save_to_file(summary, filename)
        return filename
    else:
        raise ValueError("Invalid output_type. Choose 'google_docs' or 'file'.")