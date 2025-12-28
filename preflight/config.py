"""
Configuration module - handles environment and settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Application configuration from environment variables."""
    
    def __init__(self):
        """Load environment variables."""
        load_dotenv()
    
    @staticmethod
    def get_model_name() -> str:
        """Get model name from environment or default."""
        return os.getenv("MODEL_NAME", "gemini-2.0-flash")
    
    @staticmethod
    def get_model_version() -> str:
        """Get model version from environment or default."""
        return os.getenv("MODEL_VERSION", "2.0")
    
    @staticmethod
    def get_model_url() -> str:
        """Get model API URL from environment or default."""
        return os.getenv("MODEL_URL", "https://api.google.com/v1")
    
    @staticmethod
    def get_api_key() -> str:
        """Get API key from environment."""
        return os.getenv("API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    @staticmethod
    def get_db_path() -> str:
        """Get database path from environment or default."""
        # Store in preflight/database/ folder
        default_path = Path(__file__).parent / "database" / "preflight_audit.db"
        return os.getenv("DB_PATH", str(default_path))
