#!/usr/bin/env python3
"""
AI News Briefing - Web Interface
Run this script to start the Flask web server.
"""

from web import app

if __name__ == "__main__":
    print("Starting AI News Briefing web server...")
    app.run(debug=True, host="0.0.0.0", port=5000)
