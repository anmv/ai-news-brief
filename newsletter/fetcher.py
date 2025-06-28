"""Functions for fetching newsletters from TLDR website."""

import re
from datetime import datetime, timedelta
from utils.http import make_request

def get_latest_newsletter_url():
    """
    Find the most recent TLDR AI newsletter URL.
    
    Returns:
        URL of the latest newsletter if found, None if not found
    """
    # First check today
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    today_url = f"https://tldr.tech/ai/{today_str}"
    
    print(f"Checking for today's newsletter ({today_str})...")
    
    # Don't follow redirects so we can check if it goes to the main page
    response = make_request(today_url, allow_redirects=False)
    
    if response and response.status_code == 200:
        print(f"Got it!")
        return today_url
    else:
        print(f"Nothing for today")
    
    # Then try yesterday if needed
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    yesterday_url = f"https://tldr.tech/ai/{yesterday_str}"
    
    print(f"Looking for yesterday's newsletter ({yesterday_str})...")
    
    response = make_request(yesterday_url, allow_redirects=False)
    
    if response and response.status_code == 200:
        print(f"Found one from yesterday!")
        return yesterday_url
    else:
        print(f"Nothing for yesterday either")
    
    print("No recent newsletter found.")
    return None

def fetch_newsletter(url):
    """
    Download the newsletter content.
    
    Args:
        url: The newsletter URL
        
    Returns:
        Raw HTML content of the newsletter if successful, None otherwise
    """
    if not url:
        return None
        
    print(f"Getting content from {url}...")
    
    response = make_request(url, timeout=10)
    return response.content if response else None
