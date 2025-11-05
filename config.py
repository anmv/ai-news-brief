# Configuration settings for AI Summary Engine
# Update model names here when API versions change
import os
from dotenv import load_dotenv

load_dotenv()

# Main model used for all operations
# Use the most current version available
GEMINI_MODEL = 'gemini-2.5-flash'

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

# --- Telegram Bot Configuration ---
# To enable the Telegram bot, set TELEGRAM_ENABLED to True
# and configure the bot token and user IDs.
TELEGRAM_ENABLED = os.getenv('TELEGRAM_ENABLED', 'False').lower() in ('true', '1', 't')

# Telegram Bot Token
# The token for your Telegram bot, obtained from BotFather.
# It is recommended to set this as an environment variable.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Telegram User IDs
# A comma-separated list of user IDs to send the newsletter to.
# These are the integer IDs of the users, not their usernames.
# It is recommended to set this as an environment variable.
TELEGRAM_USER_IDS = os.getenv("TELEGRAM_USER_IDS", "").split(',')

# State tracking for daily TLDR dispatches
RUN_STATE_FILE = os.getenv("RUN_STATE_FILE", "run_state.json")
