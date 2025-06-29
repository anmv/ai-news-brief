"""
AWS Lambda handler for AI News Briefing
Processes API Gateway events and returns AI-generated news briefings.
"""

import json
import os
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
import main
from ai.client import AIClient
from utils.content import sanitize_ai_content

# Load environment variables
load_dotenv()

# Set up Jinja2 template environment
template_env = Environment(loader=FileSystemLoader('web/templates'))

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    Processes API Gateway events and returns appropriate responses.
    """
    try:
        # Extract request information from API Gateway event
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        print(f"Lambda handler received: {http_method} {path}")
        
        # Route handling
        if path == '/' and http_method == 'GET':
            return handle_index()
        elif path == '/generate' and http_method == 'GET':
            return handle_generate()
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'text/html',
                    'Cache-Control': 'no-cache'
                },
                'body': render_template('error.html', error=f"Not found: {http_method} {path}"),
                'isBase64Encoded': False
            }
            
    except Exception as e:
        print(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': render_template('error.html', error=f"Internal server error: {str(e)}"),
            'isBase64Encoded': False
        }

def handle_index():
    """Handle the home page route."""
    try:
        html_content = render_template('index.html')
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': html_content,
            'isBase64Encoded': False
        }
    except Exception as e:
        print(f"Error in handle_index: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': render_template('error.html', error=f"Error loading home page: {str(e)}"),
            'isBase64Encoded': False
        }

def handle_generate():
    """Handle the newsletter generation route."""
    try:
        print("Starting newsletter generation...")
        
        # Use existing main.py functionality with web-friendly AI client
        ai_client = AIClient(web_mode=True)
        
        # Get newsletter data and create summary
        print("Collecting newsletter data...")
        newsletter_data = main.collect_newsletter_data(ai_client)
        
        print("Creating summary...")
        raw_summary = main.create_summary(newsletter_data, ai_client)
        
        # Clean and sanitize the AI-generated content
        print("Sanitizing AI content...")
        summary = sanitize_ai_content(raw_summary)
        print(f"Content sanitized, length: {len(summary)}")
        
        print("Rendering result template...")
        print(f"Summary length: {len(summary) if summary else 0}")
        print(f"Date: {newsletter_data.get('date', 'None')}")
        print(f"Newsletter URL: {newsletter_data.get('url', 'None')}")
        print(f"Article links count: {len(newsletter_data.get('article_links', []))}")
        
        # Render using proper template
        html_content = render_template(
            'result.html',
            summary=summary,
            date=newsletter_data.get('date', ''),
            newsletter_url=newsletter_data.get('url', ''),
            article_links=newsletter_data.get('article_links', [])
        )
        
        print(f"Template rendered successfully, HTML length: {len(html_content)}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': html_content,
            'isBase64Encoded': False
        }
        
    except Exception as e:
        print(f"Error in handle_generate: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': render_template('error.html', error=f"Error generating briefing: {str(e)}"),
            'isBase64Encoded': False
        }

def render_template(template_name, **kwargs):
    """
    Render a Jinja2 template with the given context.
    Mimics Flask's render_template function.
    """
    try:
        template = template_env.get_template(template_name)
        return template.render(**kwargs)
    except Exception as e:
        print(f"Template rendering error: {str(e)}")
        # Return a simple error page if template fails
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Template Error</h1>
            <p>Error rendering template '{template_name}': {str(e)}</p>
        </body>
        </html>
        """
