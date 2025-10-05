"""AI client for managing API configuration and model interactions."""

import os
import google.generativeai as genai
import requests
from google.auth.transport.requests import Request as GoogleAuthRequest
from dotenv import load_dotenv
from config import GEMINI_MODEL, API_KEY_ENV_VAR, PROXY_ENV_VAR

class ApiKeyError(Exception):
    """Exception raised when API key is missing."""
    pass

class AIClient:
    """
    Handle AI API configuration and request management.
    """
    
    def __init__(self, web_mode=False):
        """
        Initialize the AI client and configure it.
        
        Args:
            web_mode: If True, throws exceptions instead of calling exit()
        """
        self.model = None
        self.configured = False
        self.web_mode = web_mode
        self.configure()
    
    def configure(self):
        """
        Configure API key and model.
        
        Raises:
            ApiKeyError: If no API key is found (in web mode)
            SystemExit: If no API key is found (in CLI mode)
        """
        load_dotenv()
        api_key = os.getenv(API_KEY_ENV_VAR)
        proxy_url = os.getenv(PROXY_ENV_VAR)

        if not api_key:
            error_msg = f"ERROR: No API key found! Create a .env file with {API_KEY_ENV_VAR}=your_key_here"
            print(error_msg)
            
            if self.web_mode:
                raise ApiKeyError(error_msg)
            else:
                print(error_msg)
                exit()
        
        transport = None
        if proxy_url:
            print(f"Using proxy for Gemini API: {proxy_url}")
            proxies = {
                'http': proxy_url,
                'https': proxy_url,
            }
            session = requests.Session()
            session.proxies = proxies
            transport = GoogleAuthRequest(session=session)

        genai.configure(api_key=api_key, transport=transport)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        self.configured = True
        
    def generate_content(self, prompt):
        """
        Generate content using the AI model.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Response from the model
            
        Raises:
            Exception: If API call fails
        """
        if not self.configured:
            self.configure()
            
        try:
            response = self.model.generate_content(prompt)
            return response
        except Exception as e:
            print(f"ERROR in AI generation: {e}")
            raise
