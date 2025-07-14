"""
Configuration management for Merger Book MVP
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Database configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/merger_book.db')
    
    # OpenAI configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # Financial data API configuration
    POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
    YAHOO_FINANCE_ENABLED = True
    
    # File upload configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'data/uploads')
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))  # 50MB
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'doc', 'ppt'}
    
    # Application settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'merger-book-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # AI processing settings
    MAX_DOCUMENT_PAGES = 100
    PROCESSING_TIMEOUT = int(os.getenv('PROCESSING_TIMEOUT', 300))  # 5 minutes
    
    # Matching algorithm settings
    MIN_MATCH_SCORE = 0.3
    MAX_MATCHES_PER_QUERY = 50
    
    # Rate limiting
    API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', 100))  # requests per hour
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        issues = []
        
        if not cls.OPENAI_API_KEY:
            issues.append("OPENAI_API_KEY not set")
        
        if not cls.POLYGON_API_KEY:
            issues.append("POLYGON_API_KEY not set")
        
        # Create required directories
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(os.path.dirname(cls.DATABASE_PATH), exist_ok=True)
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'config': {
                'database_path': cls.DATABASE_PATH,
                'upload_folder': cls.UPLOAD_FOLDER,
                'openai_configured': bool(cls.OPENAI_API_KEY),
                'polygon_configured': bool(cls.POLYGON_API_KEY),
                'debug_mode': cls.DEBUG
            }
        }

# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DATABASE_PATH = 'data/dev_merger_book.db'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    DATABASE_PATH = ':memory:'  # In-memory database for testing
    UPLOAD_FOLDER = 'data/test_uploads'

# Configuration factory
def get_config(env: str = None) -> Config:
    """Get configuration based on environment"""
    env = env or os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return config_map.get(env, DevelopmentConfig)

