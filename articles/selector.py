"""Article selection strategies."""

import re
from ai.prompts import create_article_selection_prompt

class ArticleSelector:
    """Select relevant articles from a list of candidates."""
    
    def __init__(self, ai_client=None):
        """
        Initialize the article selector.
        
        Args:
            ai_client: AI client for smart selection
        """
        self.ai_client = ai_client
    
    def select_simple(self, potential_links, max_articles=5):
        """
        Basic selection based on unique domains and filtering.
        
        Args:
            potential_links: List of potential article links
            max_articles: Maximum number of articles to select
            
        Returns:
            List of selected article URLs
        """
        filtered = []
        seen_domains = set()
        
        for link in potential_links:
            url = link["url"]
            domain = url.split('/')[2]  # Get domain from URL
            
            if domain not in seen_domains and 'twitter' not in url and 'linkedin' not in url:
                filtered.append(url)
                seen_domains.add(domain)
            
            if len(filtered) >= max_articles:
                break
        
        return filtered
    
    def select_with_ai(self, potential_links, newsletter_text):
        """
        Use AI to select the most relevant articles.
        
        Args:
            potential_links: List of potential article links
            newsletter_text: Text content of the newsletter
            
        Returns:
            List of selected article URLs
            
        Raises:
            ValueError: If no links are found or AI selection fails
        """
        if not potential_links:
            print("No links found in the newsletter.")
            return []
        
        # If we have very few links, just return all of them
        if len(potential_links) <= 5:
            print(f"Only {len(potential_links)} links found, returning all of them")
            return [link["url"] for link in potential_links]
        
        if not self.ai_client:
            print("No AI client provided for article selection.")
            return self.select_simple(potential_links)
        
        # Create the prompt for AI selection
        prompt = create_article_selection_prompt(
            potential_links, 
            newsletter_text,
            max_chars=5000
        )
        
        # Use the AI client to generate content
        response = self.ai_client.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract the selected link numbers
        selected_numbers = []
        if "Selected:" in response_text:
            numbers_text = response_text.split("Selected:")[1].strip()
            matches = re.findall(r'\d+', numbers_text)
            selected_numbers = [int(num) for num in matches if int(num) <= len(potential_links)]
        else:
            # Try to extract any numbers
            selected_numbers = [int(num) for num in re.findall(r'\d+', response_text) 
                               if int(num) <= len(potential_links)]
        
        if not selected_numbers:
            # Don't silently fall back - make it clear there's an issue
            print("WARNING: AI didn't return any valid article numbers.")
            # Still return something useful
            return self.select_simple(potential_links)
        
        # Convert to proper indices and get URLs
        selected_indices = [num-1 for num in selected_numbers]
        selected_links = [potential_links[i]["url"] for i in selected_indices 
                         if i < len(potential_links)]
        
        # Remove duplicates
        unique_links = []
        seen = set()
        for link in selected_links:
            base_url = link.split('?')[0]
            if base_url not in seen:
                unique_links.append(link)
                seen.add(base_url)
        
        print(f"AI selected {len(unique_links)} articles for analysis")
        return unique_links
