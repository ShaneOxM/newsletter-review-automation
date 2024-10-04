# AI-Powered Newsletter Summarizer

## Overview

This project is an AI-powered newsletter summarization tool that automatically processes emails, extracts key insights, and generates comprehensive weekly summaries. It uses OpenAI's GPT models for natural language processing and Google Docs API for report generation.

## Features

- Automated email processing from a designated Gmail folder
- AI-powered content summarization using OpenAI's GPT-3.5-turbo
- Sentiment analysis of newsletter content
- Topic extraction from newsletters using LDA
- Word cloud generation for visual representation of key terms
- Weekly report generation and saving to Google Docs and local files
- Background job processing using Redis Queue
- Logging system for tracking operations and debugging

## Prerequisites

- Python 3.7+
- A Gmail account
- OpenAI API key
- Google Cloud Project with Google Docs API enabled
- Redis server

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/ai-newsletter-summarizer.git
   cd ai-newsletter-summarizer
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory with the following contents:
   ```
   EMAIL_ADDRESS=your-email@gmail.com
   EMAIL_PASSWORD=your-email-password
   IMAP_SERVER=imap.gmail.com
   NEWSLETTER_LABEL=Newsletters
   REPORT_RECIPIENT=recipient@example.com
   OPENAI_API_KEY=your-openai-api-key
   DAILY_PROCESS_TIME=09:00
   WEEKLY_REPORT_TIME=10:00
   WEEKLY_REPORT_DAY=Monday
   ```

4. Set up Google Cloud credentials:
   - Create a new project in Google Cloud Console
   - Enable the Google Docs API
   - Create credentials (OAuth 2.0 Client ID)
   - Download the client configuration and save it as `client_secret.json` in the project root

5. Install and start Redis server

## Usage

1. Start the Redis server:
   ```
   redis-server
   ```

2. Start the worker in a separate terminal:
   ```
   python worker.py
   ```

3. Run the main script:
   ```
   python main.py
   ```

The system will automatically process emails daily and generate weekly reports based on the schedule defined in the main script.

## Project Structure

- `main.py`: The main script that orchestrates the newsletter processing workflow.
- `email_handler.py`: Handles email connection and processing.
- `ai_processor.py`: Manages AI-powered summarization and analysis.
- `content_processor.py`: Handles storage and retrieval of processed content.
- `report_handler.py`: Generates and sends reports, including saving to Google Docs and local files.
- `worker.py`: Handles background job processing using Redis Queue.
- `config.py`: Contains configuration variables loaded from the .env file.
- `logger.py`: Sets up logging for the application.

## Troubleshooting

- Check the `newsletter_automation.log` file for detailed logs.
- Ensure all required environment variables are set correctly in the `.env` file.
- Verify that the Google Cloud credentials (`client_secret.json`) are set up properly.
- Make sure Redis server is running before starting the worker and main script.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.