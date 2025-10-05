# Configuration settings for AI Summary Engine
# Update model names here when API versions change

# Main model used for all operations
# Use the most current version available
GEMINI_MODEL = 'gemini-1.5-pro'

# Alternative models if needed for specific purposes
# GEMINI_LIGHT_MODEL = 'gemini-pro'  # Uncomment if needed
# GEMINI_VISION_MODEL = 'gemini-pro-vision'  # Uncomment if needed

# API configuration
API_KEY_ENV_VAR = "GEMINI_API_KEY"

# Content limits
NEWSLETTER_EXTRACT_MAX_CHARS = 5000
ARTICLE_EXTRACT_MAX_CHARS = 3000
SUMMARY_CONTENT_MAX_CHARS = 15000

# Proxy configuration for Gemini API
# Use a custom environment variable to avoid conflicts with system-wide proxies
PROXY_ENV_VAR = "HTTPS_PROXY_GEMINI"
