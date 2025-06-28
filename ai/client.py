"""AI client for managing API configuration and model interactions."""

import os
import google.generativeai as genai
from dotenv import load_dotenv
from config import GEMINI_MODEL, API_KEY_ENV_VAR

class AIClient:
    """
    Handle AI API configuration and request management.
    """
    
    def __init__(self):
        """Initialize the AI client and configure it."""
        self.model = None
        self.configured = False
        self.configure()
    
    def configure(self):
        """
        Configure API key and model.
        
        Raises:
            SystemExit: If no API key is found
        """
        load_dotenv()
        api_key = os.getenv(API_KEY_ENV_VAR)
        
        if not api_key:
            print(f"ERROR: No API key found!")
            print(f"Create a .env file with {API_KEY_ENV_VAR}=your_key_here")
            exit()
        
        genai.configure(api_key=api_key)
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
