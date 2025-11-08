#!/usr/bin/env python3
"""
AI Newsletter Summarizer Tool
June 2025 - Refactored Version
"""

import sys
import textwrap
import asyncio
from datetime import date, timedelta
from pathlib import Path

# Import modules from the refactored structure
from ai.client import AIClient
from newsletter.fetcher import get_newsletter_url_for, fetch_newsletter
from newsletter.parser import NewsletterParser
from articles.selector import ArticleSelector
from articles.extractor import extract_article_content
from ai.prompts import create_summary_prompt, create_qa_prompt
from telegram_notifications.client import send_message
from utils.run_state import RunStateStore
import config

WEEKEND_DAYS = {5, 6}  # 5 = Saturday, 6 = Sunday

def collect_newsletter_data(ai_client, target_date: date):
    """
    Collect newsletter and article data.
    
    Args:
        ai_client: The AI client for article selection
        target_date: Date for which the newsletter must be retrieved
        
    Returns:
        Dictionary with newsletter data
        
    Raises:
        RuntimeError: If newsletter can't be found or fetched
    """
    # Get newsletter URL
    newsletter_url = get_newsletter_url_for(target_date)
    if not newsletter_url:
        # Explicitly fail if the exact date is unavailable
        raise RuntimeError(
            f"No newsletter found for {target_date.isoformat()}."
        )
        
    # Get newsletter content
    html_content = fetch_newsletter(newsletter_url)
    if not html_content:
        raise RuntimeError(f"Failed to fetch newsletter from {newsletter_url}")
    
    # Parse newsletter
    parser = NewsletterParser(html_content)
    newsletter_text = parser.get_newsletter_text()
    date_str = parser.extract_date(newsletter_url)
    expected_date = target_date.isoformat()
    if date_str != expected_date:
        raise RuntimeError(
            "Newsletter date mismatch: "
            f"expected {expected_date}, got {date_str or 'unknown'}."
        )
    
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
        'date': date_str,
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

async def send_telegram_summary(summary, date_str):
    """
    Sends the summary to Telegram users if enabled.

    Args:
        summary: The summary text to send.
        date_str: ISO date string of the newsletter.
    """
    if not config.TELEGRAM_ENABLED:
        print("Telegram notifications disabled; skipping send.")
        return False

    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_USER_IDS:
        print("Telegram is enabled, but token or user IDs are missing.")
        return False

    # Format the message - summary already contains HTML formatting
    message = summary

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

    if not tasks:
        print("No valid Telegram user IDs configured; skipping send.")
        return False

    print(f"Sending summary for {date_str} to {len(tasks)} Telegram user(s)...")
    await asyncio.gather(*tasks)
    print("Summary sent successfully via Telegram.")
    return True

async def process_and_send_for_date(
    target_date: date,
    ai_client: AIClient,
    state_store: RunStateStore,
) -> bool:
    """Process newsletter workflow for a single date."""
    print(f"\n=== Обработка новостей за {target_date.isoformat()} началась ===")
    try:
        newsletter_data = collect_newsletter_data(ai_client, target_date)
        summary = create_summary(newsletter_data, ai_client)

        # print("\n" + "=" * 80)
        # print(f"AI BRIEFING - TLDR NEWSLETTER {newsletter_data['date']}")
        # print("=" * 80)
        # print(summary)
        # print("\n" + "=" * 80)

        sent = await send_telegram_summary(summary, newsletter_data["date"])
        if sent:
            state_store.mark_run(target_date)
            print(f"Статус: рассылка за {target_date.isoformat()} завершена.")
            return True

        print(
            "Telegram delivery did not complete; state not recorded. "
            f"Пропустите дату {target_date.isoformat()} вручную при необходимости."
        )
        return False

    except RuntimeError as exc:
        print(f"INFO: {exc}")
        print(
            f"Новостей за {target_date.isoformat()} нет или источник недоступен. "
            "Состояние не обновлено."
        )
        return False

async def main():
    """
    Main asynchronous function that runs everything.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    state_store = RunStateStore(Path(config.RUN_STATE_FILE))
    end_date = date.today()
    last_run_date = state_store.get_last_run_date()

    if last_run_date is None:
        start_date = end_date - timedelta(days=7)
    else:
        start_date = last_run_date + timedelta(days=1)

    if start_date > end_date:
        print(
            "Актуальных дат для обработки нет. Последняя рассылка уже отправлена."
        )
        return 0

    dates_to_process = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() not in WEEKEND_DAYS:
            dates_to_process.append(current_date)
        current_date += timedelta(days=1)

    if not dates_to_process:
        print(
            "Нет новых рабочих дней для обработки. Все рассылки актуальны."
        )
        return 0

    print("Даты к обработке:", ", ".join(d.isoformat() for d in dates_to_process))

    try:
        ai_client = AIClient()
        for index, target_date in enumerate(dates_to_process):
            await process_and_send_for_date(target_date, ai_client, state_store)
            if index < len(dates_to_process) - 1:
                await asyncio.sleep(10)
        return 0

    except Exception as exc:
        print(f"\nERROR: {str(exc)}")
        print("The program encountered an error and cannot continue.")
        return 1

if __name__ == "__main__":
    # Run the main async function
    sys.exit(asyncio.run(main()))
