"""
Route definitions for the AI News Briefing web interface.
Minimal version with essential functionality.
"""

import os
from flask import render_template
from web import app
import main
from dotenv import load_dotenv

@app.route('/')
def index():
    """Render the home page."""
    # Simple check if API key exists
    load_dotenv()
    has_api_key = bool(os.getenv("GEMINI_API_KEY"))
    return render_template('index.html', has_api_key=has_api_key)

@app.route('/generate')
def generate_briefing():
    """Generate a news briefing and display it."""
    try:
        # Use existing main.py functionality with web-friendly AI client
        from ai.client import AIClient
        ai_client = AIClient(web_mode=True)
        
        # Get newsletter data and create summary
        newsletter_data = main.collect_newsletter_data(ai_client)
        summary = main.create_summary(newsletter_data, ai_client)
        
        # Display results
        return render_template(
            'result.html',
            summary=summary,
            date=newsletter_data.get('date', ''),
            newsletter_url=newsletter_data.get('url', ''),
            article_links=newsletter_data.get('article_links', [])
        )
        
    except Exception as e:
        return render_template('error.html', error=str(e))
