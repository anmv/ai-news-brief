# main.py
# My AI Newsletter Summarizer Tool
# June 2025

import os
import re
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
import textwrap

# The first version of this worked but didn't handle API key errors well
# Decided to add better error handling after a few failed runs
def configure_api():
    """Sets up API key for Gemini"""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: No API key found!")
        print("Create a .env file with GEMINI_API_KEY=your_key_here")
        exit()
    genai.configure(api_key=api_key)

def get_latest_tldr_url():
    """Finds most recent TLDR newsletter"""
    # TODO: Maybe add check for weekend issues?
    from datetime import datetime, timedelta
    
    # Basic headers to avoid getting blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # First check today
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    today_url = f"https://tldr.tech/ai/{today_str}"
    
    print(f"Checking for today's newsletter ({today_str})...")
    try:
        response = requests.get(today_url, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"Got it!")
            return today_url
        else:
            print(f"Nothing for today (status: {response.status_code})")
    except Exception as e:
        print(f"Error: {e}")
    
    # Then try yesterday if needed
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    yesterday_url = f"https://tldr.tech/ai/{yesterday_str}"
    
    print(f"Looking for yesterday's newsletter ({yesterday_str})...")
    try:
        # print(f"DEBUG: trying {yesterday_url}")  # Left this in from debugging
        response = requests.get(yesterday_url, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"Found one from yesterday!")
            return yesterday_url
        else:
            print(f"Nothing for yesterday either (status: {response.status_code})")
    except Exception as e:
        print(f"Error: {e}")
    
    # Fallback - AI suggested using a specific test date which was helpful
    # TODO: Remove
    print("Nothing recent found. Using backup date for testing.")
    test_date = "2025-06-27"
    return f"https://tldr.tech/ai/{test_date}"

def get_article_links(soup):
    """Gets all the links from the newsletter"""
    links = []
    all_links = soup.find_all('a')
    
    # My original version was simpler but missed some good articles
    # all_hrefs = [a.get('href') for a in all_links if a.get('href') and 'twitter' not in a.get('href')]
    # return all_hrefs[:10]  # Just grabbed first 10 links
    
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
                
                # Get text around link for context - AI suggested this approach
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

# My original simple link selectionI
def select_links_simple(potential_links):
    """Basic selection of links - my first version"""
    # Just grab the first 5 non-social links
    filtered = []
    seen_domains = set()
    
    for link in potential_links:
        url = link["url"]
        domain = url.split('/')[2]  # Get domain from URL
        
        if domain not in seen_domains and 'twitter' not in url and 'linkedin' not in url:
            filtered.append(url)
            seen_domains.add(domain)
        
        if len(filtered) >= 5:
            break
    
    return filtered

# Enhanced to be smarter about selection criteria
# TODO: Test if this is actually reliable
def select_relevant_article_links(potential_links, newsletter_text, model):
    """Uses AI to pick the best articles from the newsletter"""
    if not potential_links:
        return []
    
    # First try simple selection if we have few links
    if len(potential_links) <= 5:
        print("Not many links, using simple selection")
        return select_links_simple(potential_links)
    
    # Extract URLs and contexts for the prompt
    link_data = []
    for i, link in enumerate(potential_links):
        link_data.append(f"{i+1}. URL: {link['url']}\n   Context: {link['context']}")
    
    links_text = "\n\n".join(link_data)
    
    # Simpler prompt that worked better than my original long one
    prompt = f"""
    Find 5-8 relevant articles about AI tech and research from this newsletter:
    {newsletter_text[:5000]}

    Here are the links:
    {links_text}

    Just return the numbers of the best articles (format: "Selected: 1, 3, 5, 7, 8")
    """
    
    try:
        # Using smaller model to save on API costs
        selection_model = genai.GenerativeModel('gemini-1.0-pro')
        response = selection_model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract the selected link numbers
        selected_numbers = []
        if "Selected:" in response_text:
            numbers_text = response_text.split("Selected:")[1].strip()
            import re
            matches = re.findall(r'\d+', numbers_text)
            selected_numbers = [int(num) for num in matches if int(num) <= len(potential_links)]
        else:
            # Try to extract any numbers
            import re
            selected_numbers = [int(num) for num in re.findall(r'\d+', response_text) if int(num) <= len(potential_links)]
        
        # Fallback if AI messes up
        if not selected_numbers:
            print("AI selection failed. Using first 5 links instead.")
            selected_numbers = list(range(1, min(6, len(potential_links)+1)))
        
        # Convert to proper indices
        selected_indices = [num-1 for num in selected_numbers]
        selected_links = [potential_links[i]["url"] for i in selected_indices if i < len(potential_links)]
        
        # Remove duplicates
        unique_links = []
        seen = set()
        for link in selected_links:
            base_url = link.split('?')[0]
            if base_url not in seen:
                unique_links.append(link)
                seen.add(base_url)
        
        print(f"Found {len(unique_links)} good articles for analysis")
        return unique_links
        
    except Exception as e:
        print(f"Error in AI selection: {e}")
        print("Falling back to simple selection")
        # Just use my original simple method as backup
        return select_links_simple(potential_links)

def extract_article_content(url, timeout=15):
    """Grabs content from article URLs"""
    # I initially used a 5 second timeout but kept getting timeouts
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Find main content
        article = soup.find('article')
        if not article:
            # Look for other containers
            for container in ['main', 'div[class*="content"]', 'div[class*="article"]', 'div[role="main"]']:
                article = soup.select_one(container)
                if article:
                    break
        
        # Last resort
        if not article:
            article = soup.find('body')
        
        if article:
            text = article.get_text(separator='\n', strip=True)
            # Limit length - I was hitting token limits before this
            max_chars = 3000
            if len(text) > max_chars:
                text = text[:max_chars] + "... [content truncated]"
            return text
        
        return None
        
    except Exception as e:
        print(f"Error with {url}: {e}")
        return None

def get_newsletter_content(url):
    """Gets the newsletter and article content"""
    if not url: 
        return None
        
    print(f"Getting content from {url}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get date from URL
        match = re.search(r'/ai/(\d{4}-\d{2}-\d{2})$', url)
        date = match.group(1) if match else "Unknown date"
        
        # Find main content
        main_content = soup.find('div', {'class': 'max-w-3xl'})
        if not main_content:
            main_content = soup.find('main')
            if not main_content:
                main_content = soup.find('body')
        
        if main_content:
            newsletter_text = main_content.get_text(separator='\n', strip=True)
            
            print("Finding article links...")
            # Get links
            potential_links = get_article_links(soup)
            print(f"Found {len(potential_links)} links in newsletter")
            
            # Select best links - tried doing this manually at first
            # but AI does a much better job
            model = genai.GenerativeModel('gemini-1.0-pro')
            relevant_links = select_relevant_article_links(potential_links, newsletter_text, model)
            print(f"Selected {len(relevant_links)} best articles")
            
            # Get content from each article
            article_contents = []
            for i, link in enumerate(relevant_links):
                print(f"Reading article {i+1}/{len(relevant_links)}: {link}")
                content = extract_article_content(link)
                if content:
                    article_title = f"ARTICLE {i+1}: {link}"
                    article_contents.append(f"\n\n{article_title}\n{'-' * len(article_title)}\n{content}")
            
            # Put it all together
            all_content = f"{newsletter_text}\n\n{'=' * 40}\nARTICLE CONTENTS\n{'=' * 40}\n"
            all_content += "\n".join(article_contents)
            
            print(f"Got newsletter and {len(article_contents)} articles")
            
            return {
                'date': date,
                'url': url,
                'content': all_content,
                'article_links': relevant_links
            }
        else:
            # This can happen when structure changes
            raise Exception("Can't find newsletter content")
            
    except Exception as e:
        print(f"ERROR: Failed to get newsletter: {e}")
        return None

def summarize_content(newsletter_data, model):
    """Creates an AI summary of the newsletter"""
    if not newsletter_data:
        return "No newsletter content found."
    
    print(f"Creating summary for {newsletter_data['date']}...")
    
    # Need to truncate for token limits
    content = newsletter_data['content']
    max_chars = 15000  # TODO: Right limit?
    if len(content) > max_chars:
        content = content[:max_chars] + "... [content truncated]"
    
    # TODO: Prompt Engineering
    prompt = f"""
    Summarize this TLDR AI newsletter from {newsletter_data['date']}.
    Focus on the 3-5 biggest AI developments, including:
    - Main innovations
    - How businesses might use them
    - How realistic they are
    - Why they matter for AI teams
    
    Use headings and bullet points. Keep it under 800 words.
    
    NEWSLETTER CONTENT:
    {content}
    """
    
    try:
        try:
            # Try main model 
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            # This happens sometimes with the big model
            print(f"Model error: {str(e)[:100]}...")
            print("Trying smaller model instead...")
            fallback_model = genai.GenerativeModel('gemini-1.0-pro')
            response = fallback_model.generate_content(prompt)
            return response.text
    except Exception as e:
        print(f"ERROR: Summary failed: {e}")
        return f"Can't create summary - API error: {str(e)}"

def main():
    """Main function that runs everything"""
    configure_api()
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    # Get newsletter URL
    newsletter_url = get_latest_tldr_url()
    if not newsletter_url:
        print("\nCan't continue - no newsletter found.")
        return
        
    # Get content
    newsletter_data = get_newsletter_content(newsletter_url)
    if not newsletter_data:
        print("\nCan't continue - couldn't get newsletter content.")
        return
    
    # Make summary
    summary = summarize_content(newsletter_data, model)
    
    # Show results
    print("\n" + "="*80)
    print(f"AI BRIEFING - TLDR NEWSLETTER {newsletter_data['date']}")
    print("="*80)
    print(summary)
    print("\n" + "="*80)

    # Q&A part
    print("\nQ&A mode - type 'quit', 'exit', or 'q' to stop.")
    
    # Using smaller model for Q&A to avoid rate limits
    qa_model = genai.GenerativeModel('gemini-1.0-pro')
    
    while True:
        question = input("\nQuestion about the newsletter: ")
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        print("Thinking...")
        try:
            qa_prompt = f"""
            Answer this question about the TLDR AI newsletter from {newsletter_data['date']}.
            If you can't answer from the newsletter, just say so.
            Be concise.
            
            NEWSLETTER CONTENT:
            {newsletter_data['content']}
            
            QUESTION:
            {question}
            """
            
            try:
                # Try main model first
                response = model.generate_content(qa_prompt)
            except Exception as e:
                print(f"Using backup model... ({str(e)[:50]})")
                response = qa_model.generate_content(qa_prompt)
                
            # Format output nicely
            wrapped_text = textwrap.fill(response.text, width=80)
            print(f"\nANSWER:\n{wrapped_text}")
            
        except Exception as e:
            print(f"\nERROR: {e}")
            print("Might be API limits or connection issues.")

if __name__ == "__main__":
    main()
