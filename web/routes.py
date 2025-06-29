"""
Route definitions for the AI News Briefing web interface.
Minimal version with essential functionality.
"""

from flask import render_template
from web import app
import main
from ai.client import AIClient

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/generate')
def generate_briefing():
    """Generate a news briefing and display it."""
    try:
        # Use existing main.py functionality with web-friendly AI client
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
