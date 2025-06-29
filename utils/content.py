"""Content processing utilities shared between Flask and Lambda handlers."""

def sanitize_ai_content(content):
    """
    Sanitize AI-generated content to remove problematic characters.
    Used by both Flask routes and Lambda handler.
    """
    if not content:
        return content
    
    try:
        # Remove or replace problematic Unicode characters
        # First, encode to bytes then decode with error handling
        content_bytes = content.encode('utf-8', errors='ignore')
        clean_content = content_bytes.decode('utf-8', errors='ignore')
        
        # Remove any remaining replacement characters
        clean_content = clean_content.replace('\ufffd', '')
        
        # Remove any null bytes or other control characters that might cause issues
        clean_content = ''.join(char for char in clean_content if ord(char) >= 32 or char in '\n\r\t')
        
        print(f"Content sanitization: {len(content)} -> {len(clean_content)} characters")
        return clean_content
        
    except Exception as e:
        print(f"Error sanitizing content: {str(e)}")
        # Return a safe fallback
        return "Content sanitization failed - displaying truncated summary."
