"""Functions for fetching newsletters from TLDR website."""

from __future__ import annotations

from datetime import date
from typing import Optional

from utils.http import make_request


def get_newsletter_url_for(target_date: date) -> Optional[str]:
    """Return the TLDR AI newsletter URL for ``target_date`` if it exists."""

    date_str = target_date.strftime("%Y-%m-%d")
    url = f"https://tldr.tech/ai/{date_str}"

    response = make_request(url, allow_redirects=False)
    if response and response.status_code == 200:
        print(f"Found newsletter for {date_str}.")
        return url

    print(f"No newsletter available for {date_str}.")
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
