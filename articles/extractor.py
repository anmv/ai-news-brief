"""Article content extraction."""

from bs4 import BeautifulSoup
from utils.http import make_request
from utils.text import truncate_text

def extract_article_content(url, timeout=15, max_chars=None):
    """
    Extract main content from an article URL.
    
    Args:
        url: The article URL
        timeout: Request timeout in seconds
        max_chars: Maximum characters to extract
        
    Returns:
        Extracted article content if successful, None otherwise
    """
    try:
        response = make_request(url, timeout=timeout)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove non-content elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Find main content element
        article = soup.find('article')
        if not article:
            # Look for other containers
            for container in ['main', 'div[class*="content"]', 'div[class*="article"]', 'div[role="main"]']:
                article = soup.select_one(container)
                if article:
                    break
        
        # Last resort: use body if other containers not found
        if not article:
            article = soup.find('body')
        
        if article:
            text = article.get_text(separator='\n', strip=True)
            
            # Limit length if specified
            if max_chars and len(text) > max_chars:
                text = truncate_text(text, max_chars)
                
            return text
            
        return None
        
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None
