"""HTTP utility functions for making requests."""

import requests

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def make_request(url, timeout=10, allow_redirects=True, headers=None):
    """
    Make HTTP request with consistent error handling.
    
    Args:
        url: URL to request
        timeout: Request timeout in seconds
        allow_redirects: Whether to follow redirects
        headers: Optional custom headers
        
    Returns:
        Response content if successful, None otherwise
    """
    try:
        request_headers = headers or DEFAULT_HEADERS
        response = requests.get(
            url, 
            headers=request_headers, 
            timeout=timeout, 
            allow_redirects=allow_redirects
        )
        response.raise_for_status()
        return response
    except Exception as e:
        print(f"Error requesting {url}: {e}")
        return None
