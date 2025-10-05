#!/usr/bin/env python3
"""
AI Newsletter Summarizer Tool
June 2025 - Refactored Version
"""

import sys
import textwrap
import asyncio

# Import modules from the refactored structure
from ai.client import AIClient
from newsletter.fetcher import get_latest_newsletter_url, fetch_newsletter
from newsletter.parser import NewsletterParser
from articles.selector import ArticleSelector
from articles.extractor import extract_article_content
from ai.prompts import create_summary_prompt, create_qa_prompt
from telegram.client import send_message
import config

def collect_newsletter_data(ai_client):
    """
    Collect newsletter and article data.
    
    Args:
        ai_client: The AI client for article selection
        
    Returns:
        Dictionary with newsletter data
        
    Raises:
        RuntimeError: If newsletter can't be found or fetched
    """
    # Get newsletter URL
    newsletter_url = get_latest_newsletter_url()
    if not newsletter_url:
        # Fail directly instead of providing fallbacks that may hide issues
        raise RuntimeError("No newsletter found for today or yesterday.")
        
    # Get newsletter content
    html_content = fetch_newsletter(newsletter_url)
    if not html_content:
        raise RuntimeError(f"Failed to fetch newsletter from {newsletter_url}")
    
    # Parse newsletter
    parser = NewsletterParser(html_content)
    newsletter_text = parser.get_newsletter_text()
    date = parser.extract_date(newsletter_url)
    
    # Extract potential links
    potential_links = parser.extract_links()
    print(f"Found {len(potential_links)} links in newsletter")
    
    # Select best links
    selector = ArticleSelector(ai_client)
    relevant_links = selector.select_with_ai(potential_links, newsletter_text)
    print(f"Selected {len(relevant_links)} best articles")
    
    # Get content from each article
    article_contents = []
    for i, link in enumerate(relevant_links):
        print(f"Reading article {i+1}/{len(relevant_links)}: {link}")
        content = extract_article_content(
            link, 
            timeout=15,
            max_chars=config.ARTICLE_EXTRACT_MAX_CHARS
        )
        if content:
            article_title = f"ARTICLE {i+1}: {link}"
            article_contents.append(f"\n\n{article_title}\n{'-' * len(article_title)}\n{content}")
    
    # Put it all together
    all_content = f"{newsletter_text}\n\n{'=' * 40}\nARTICLE CONTENTS\n{'=' * 40}\n"
    all_content += "\n".join(article_contents)
    
    return {
        'date': date,
        'url': newsletter_url,
        'content': all_content,
        'article_links': relevant_links
    }

def create_summary(newsletter_data, ai_client):
    """
    Create AI summary of newsletter content.
    
    Args:
        newsletter_data: Dictionary with newsletter content
        ai_client: The AI client for summarization
        
    Returns:
        Summary text string
        
    Raises:
        RuntimeError: If summary creation fails
    """
    print(f"Creating summary for {newsletter_data['date']}...")
    
    prompt = create_summary_prompt(
        newsletter_data, 
        newsletter_data['date']
    )
    
    response = ai_client.generate_content(prompt)
    return response.text

def run_qa_mode(newsletter_data, ai_client):
    """
    Run interactive Q&A session about the newsletter.
    
    Args:
        newsletter_data: Dictionary with newsletter content
        ai_client: The AI client for Q&A
    """
    print("\nQ&A mode - type 'quit', 'exit', or 'q' to stop.")
    print("\nPress Enter to start Q&A mode...")
    input()
    
    while True:
        try:
            # Get user question
            question = input("\nQuestion about the newsletter: ")
            if question.lower() in ['quit', 'exit', 'q']:
                break
                
            # Skip empty questions
            if not question.strip():
                continue
            
            print("Thinking...")
            prompt = create_qa_prompt(
                question, 
                newsletter_data['content'], 
                newsletter_data['date']
            )
            
            response = ai_client.generate_content(prompt)
                
            # Format output nicely
            wrapped_text = textwrap.fill(response.text, width=80)
            print(f"\nANSWER:\n{wrapped_text}")
            
        except Exception as e:
            print(f"\nERROR: {e}")
            print("Might be API limits or connection issues.")

async def send_telegram_summary(summary, date):
    """
    Sends the summary to Telegram users if enabled.

    Args:
        summary: The summary text to send.
        date: The date of the newsletter.
    """
    if config.TELEGRAM_ENABLED:
        if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_USER_IDS:
            print("Telegram is enabled, but token or user IDs are missing.")
            return

        # Format the message with a title and pre-formatted text
        message = f"<b>AI Briefing - {date}</b>\n\n<pre>{summary}</pre>"

        # Create a list of tasks for sending messages
        tasks = []
        for user_id in config.TELEGRAM_USER_IDS:
            if user_id:  # Ensure user_id is not an empty string
                tasks.append(
                    send_message(
                        user_id=int(user_id),
                        message_text=message,
                        bot_token=config.TELEGRAM_BOT_TOKEN
                    )
                )

        # Run all sending tasks concurrently
        if tasks:
            print(f"Sending summary to {len(tasks)} Telegram user(s)...")
            await asyncio.gather(*tasks)
            print("Summary sent successfully via Telegram.")

async def main():
    """
    Main asynchronous function that runs everything.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Initialize AI client
        ai_client = AIClient()
        
        # Collect newsletter data
        newsletter_data = collect_newsletter_data(ai_client)
        
        # Create summary
        summary = create_summary(newsletter_data, ai_client)
        
        # Show results
        print("\n" + "="*80)
        print(f"AI BRIEFING - TLDR NEWSLETTER {newsletter_data['date']}")
        print("="*80)
        print(summary)
        print("\n" + "="*80)
    
        # Send summary via Telegram
        await send_telegram_summary(summary, newsletter_data['date'])

        # Run Q&A mode
        run_qa_mode(newsletter_data, ai_client)
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("The program encountered an error and cannot continue.")
        return 1

if __name__ == "__main__":
    # Run the main async function
    sys.exit(asyncio.run(main()))
