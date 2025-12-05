"""
Configuration settings for LinkedIn Recruiter Finder
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class"""
    
    # API Keys
    GOOGLE_CUSTOM_SEARCH_API_KEY = os.getenv('GOOGLE_CUSTOM_SEARCH_API_KEY')
    GOOGLE_CUSTOM_SEARCH_ENGINE_ID = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
    GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
    
    # Application Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # File Upload Settings
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt'}
    ALLOWED_MIME_TYPES = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    ]
    
    # Search Settings
    MAX_SEARCH_RESULTS = 10
    SEARCH_TIMEOUT = 30
    
    # Gemini Model Settings
    GEMINI_MODEL = 'gemini-2.0-flash-exp'
    GEMINI_TEMPERATURE = 0.1
    GEMINI_MAX_OUTPUT_TOKENS = 1000
    GEMINI_TOP_P = 0.8
    GEMINI_TOP_K = 40
    
    @property
    def api_keys_configured(self):
        """Check if all required API keys are configured"""
        return all([
            self.GOOGLE_CUSTOM_SEARCH_API_KEY,
            self.GOOGLE_CUSTOM_SEARCH_ENGINE_ID,
            self.GOOGLE_GEMINI_API_KEY
        ])
    
    @property
    def custom_search_configured(self):
        """Check if Google Custom Search API is configured"""
        return all([
            self.GOOGLE_CUSTOM_SEARCH_API_KEY,
            self.GOOGLE_CUSTOM_SEARCH_ENGINE_ID
        ])
    
    @property
    def gemini_configured(self):
        """Check if Gemini API is configured"""
        return bool(self.GOOGLE_GEMINI_API_KEY) 