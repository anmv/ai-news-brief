"""
Web interface module for AI News Briefing.
This package provides a Flask web interface to the news briefing functionality.
"""

from flask import Flask

# Create Flask application instance
app = Flask(__name__)
# TODO: Replace SECRET_KEY with secure random key from environment variable in production
app.config.update(
    SECRET_KEY="dev-key-change-in-production"
)

# Import routes after app is created to avoid circular imports
from web import routes  # noqa
