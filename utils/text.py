"""Text utility functions for processing text content."""

def truncate_text(text, max_length, suffix="... [content truncated]"):
    """
    Truncate text to a maximum length with a suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length to allow
        suffix: Suffix to append when truncating
    
    Returns:
        Truncated text with suffix if needed, or original text
    """
    if not text:
        return ""
        
    if len(text) <= max_length:
        return text
        
    return text[:max_length] + suffix
