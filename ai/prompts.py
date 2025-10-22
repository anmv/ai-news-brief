"""Prompt template management for AI interactions."""

from config import SUMMARY_CONTENT_MAX_CHARS
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
    Create a strategic AI news briefing for IT Specialists, Businessmen, and Programmers based on this TLDR AI newsletter. from {date}.

    CRITICAL: Preserve the actual news content - specific company names, product launches, research findings, and concrete developments. Don't turn everything into abstract concepts.

    For each significant news item, provide:

    <b>🔹 [Specific headline - use actual company/product names]</b>

    <b>Что произошло:</b> [Detailed factual summary - provide comprehensive context about who did what, when, how, and with what specific details. For unfamiliar companies or concepts, include brief definitions (e.g., "CoreWeave, a cloud service provider specializing in AI infrastructure, announced..."). Include technical specifications, timelines, and background context.]

    <b>Почему важно:</b> [Explain the strategic importance AND what specific problem this solves or opportunity it creates. Address both immediate business impact and longer-term implications for AI/ML teams and competitive positioning.]

    <b>Действия:</b> [Specific next steps - evaluate, pilot, monitor, invest, or ignore - with clear rationale]

    WRITING GUIDELINES:
    - Use actual company names (OpenAI, Google, Microsoft, Anthropic, etc.)
    - For lesser-known companies, provide brief context (e.g., "Sakana AI, a Tokyo-based AI research company,...")
    - Include specific products, features, numbers, dates, and technical details
    - Preserve research findings and their implications
    - Make "What Happened" sections comprehensive - don't just summarize, provide full context
    - In "Why It Matters", always explain what problem is being solved or opportunity created
    - Выдавать пользователю новости на русском языке

    AUDIENCE: Technical managers, IT specialists, programmers who need comprehensive news facts AND strategic context to make informed decisions.

    FORMATTING:
    - Generate clean text with ONLY <b> for bold and <i> for italic when needed
    - Start with: <b>📰 AI News Briefing - {date}</b>
    - Use emoji 🔹 for bullet points/news items
    - Separate sections with double line breaks (NOT <br> tags!)
    - Keep under 800 words to fit Telegram message limits
    - Focus on 4-5 most important developments
    - Professional, informative tone
    - NO HTML tags except <b> and <i>
    - NO <p>, <br>, <div>, <h1-h6> or any other HTML tags

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
