"""Parser for TLDR newsletter content."""

import re
from bs4 import BeautifulSoup
from config import NEWSLETTER_EXTRACT_MAX_CHARS
from utils.text import truncate_text

class NewsletterParser:
    """Parse newsletter content and extract relevant information."""

    def __init__(self, html_content):
        """
        Initialize the newsletter parser.
        
        Args:
            html_content: Raw HTML content of the newsletter
        """
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.content_text = None
        self._parse_content()

    def _parse_content(self):
        """Extract main content text from the newsletter."""
        # Find main content
        main_content = self.soup.find('div', {'class': 'max-w-3xl'})
        if not main_content:
            main_content = self.soup.find('main')
            if not main_content:
                main_content = self.soup.find('body')
        
        if main_content:
            self.content_text = main_content.get_text(separator='\n', strip=True)
            # Truncate if too long
            self.content_text = truncate_text(
                self.content_text, 
                NEWSLETTER_EXTRACT_MAX_CHARS
            )
        else:
            self.content_text = ""
            print("WARNING: Could not find main content in newsletter.")

    def extract_links(self):
        """
        Extract all potential article links from the newsletter.
        
        Returns:
            List of dictionaries with link URLs and context
        """
        links = []
        all_links = self.soup.find_all('a')
        
        for link in all_links:
            href = link.get('href')
            # Filter for actual article links
            if href and href.startswith('http') and 'tldr.tech' not in href:
                # Skip social media and subscription stuff
                if ('twitter.com' not in href and 
                    'facebook.com' not in href and 
                    'linkedin.com' not in href and
                    'subscribe' not in href.lower() and
                    'utm_source=tldrai' in href):  # This suggests it's an article
                    
                    # Get text around link for context
                    surrounding_text = ""
                    parent = link.parent
                    if parent:
                        surrounding_text = parent.get_text().strip()
                    
                    links.append({
                        "url": href,
                        "text": link.get_text().strip(),
                        "context": surrounding_text if surrounding_text else link.get_text().strip()
                    })
        
        return links
        
    def get_newsletter_text(self):
        """
        Get the newsletter text content.
        
        Returns:
            Extracted text content from the newsletter
        """
        return self.content_text
        
    def extract_date(self, url):
        """
        Get date from newsletter URL.
        
        Args:
            url: Newsletter URL
            
        Returns:
            Date string in YYYY-MM-DD format or "Unknown date"
        """
        match = re.search(r'/ai/(\d{4}-\d{2}-\d{2})$', url)
        return match.group(1) if match else "Unknown date"
