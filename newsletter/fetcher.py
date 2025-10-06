"""Functions for fetching newsletters from TLDR website."""

from datetime import datetime, timedelta
from utils.http import make_request

def get_latest_newsletter_url():
    """
    Find the most recent TLDR AI newsletter URL.
    Checks up to 7 days back to handle weekends and holidays.
    
    Returns:
        URL of the latest newsletter if found, None if not found
    """
    today = datetime.now()
    
    # Check up to 7 days back
    for days_back in range(7):
        check_date = today - timedelta(days=days_back)
        date_str = check_date.strftime("%Y-%m-%d")
        url = f"https://tldr.tech/ai/{date_str}"
        
        day_name = check_date.strftime("%A")
        print(f"Checking for {day_name}'s newsletter ({date_str})...")
        
        # Don't follow redirects so we can check if it goes to the main page
        response = make_request(url, allow_redirects=False)
        
        if response and response.status_code == 200:
            print(f"Found newsletter from {day_name} ({date_str})!")
            return url
        else:
            print(f"Nothing for {day_name}")
    
    print("No newsletter found in the past week.")
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
