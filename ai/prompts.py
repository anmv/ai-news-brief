"""Prompt template management for AI interactions."""

from config import NEWSLETTER_EXTRACT_MAX_CHARS, SUMMARY_CONTENT_MAX_CHARS
from utils.text import truncate_text

def create_article_selection_prompt(links, newsletter_text, max_chars=None):
    """
    Create a prompt for selecting articles.
    
    Args:
        links: List of potential links with context
        newsletter_text: The newsletter content
        max_chars: Maximum characters for newsletter text
        
    Returns:
        A prompt string for article selection
    """
    # Extract URLs and contexts for the prompt
    link_data = []
    for i, link in enumerate(links):
        link_data.append(f"{i+1}. URL: {link['url']}\n   Context: {link['context']}")
    
    links_text = "\n\n".join(link_data)
    
    # Truncate newsletter text if needed
    truncated_text = newsletter_text
    if max_chars:
        truncated_text = truncate_text(newsletter_text, max_chars)
    
    # Construct the prompt
    prompt = f"""
    Find 5-8 relevant articles about AI tech and research from this newsletter:
    {truncated_text}

    Here are the links:
    {links_text}

    Just return the numbers of the best articles (format: "Selected: 1, 3, 5, 7, 8")
    """
    
    return prompt

def create_summary_prompt(newsletter_data, date):
    """
    Create a prompt for newsletter summarization.
    
    Args:
        newsletter_data: Dictionary with newsletter content and links
        date: The newsletter date
        
    Returns:
        A prompt string for summarization
    """
    content = truncate_text(
        newsletter_data['content'], 
        SUMMARY_CONTENT_MAX_CHARS
    )
    
    prompt = f"""
    You are creating a strategic AI news briefing specifically for Applied Science Managers and Data Science Managers.
    
    Transform this generic TLDR AI newsletter from {date} into actionable management insights. Focus on the 3-5 most strategically important developments for team leaders.
    
    For each development, provide:
    - <strong>Strategic Impact:</strong> Why this matters for Applied Science/Data Science teams
    - <strong>Management Implications:</strong> Resource allocation, hiring needs, technology adoption decisions
    - <strong>Implementation Reality:</strong> Timeline, feasibility, and what it means for current projects
    - <strong>Competitive Positioning:</strong> How this affects your team's capabilities vs. industry standards
    - <strong>Action Items:</strong> Specific recommendations for managers (explore, invest, ignore, prepare)
    
    AUDIENCE: Applied Science Managers and Data Science Managers who need to make strategic decisions about AI/ML technologies, team direction, and resource allocation.
    
    FORMATTING REQUIREMENTS - Generate clean HTML:
    - Use <h2> for main section headers
    - Use <h3> for sub-headers (numbered items like "1. Development Title")
    - Use <strong> for emphasis instead of **bold**
    - Use <p> for paragraphs
    - Keep content concise and scannable for busy managers
    - Under 800 words total
    - Executive-level, strategic tone
    
    NEWSLETTER CONTENT:
    {content}
    """
    
    return prompt

def create_qa_prompt(question, newsletter_content, date):
    """
    Create a prompt for Q&A about the newsletter.
    
    Args:
        question: User question
        newsletter_content: The newsletter content
        date: The newsletter date
        
    Returns:
        A prompt string for Q&A
    """
    truncated_content = truncate_text(
        newsletter_content,
        SUMMARY_CONTENT_MAX_CHARS
    )
    
    prompt = f"""
    Answer this question about the TLDR AI newsletter from {date}.
    First try to answer using the newsletter content.
    If the newsletter doesn't contain information to answer the question, use your general knowledge to provide a helpful response.
    Be concise but thorough.
    
    NEWSLETTER CONTENT:
    {truncated_content}
    
    QUESTION:
    {question}
    """
    
    return prompt
