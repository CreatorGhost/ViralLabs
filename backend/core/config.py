"""
Application configuration and directory setup.
Single Responsibility: Only handles configuration.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    youtube_api_key: Optional[str] = None
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Database settings
    database_url: str = "postgresql+asyncpg://adityapratapsingh@localhost:5432/youtuber"
    database_echo: bool = False  # Set to True for SQL query logging
    
    # JWT settings
    jwt_secret_key: str = "your-super-secret-key-change-in-production"  # Change in production!
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 10
    max_sessions_per_user: int = 5  # Max active refresh tokens
    
    # Model defaults
    default_script_model: str = "gpt-5.1"
    default_refine_model: str = "gpt-5-nano"
    default_thumbnail_model: str = "gemini-3-pro-image-preview"
    
    # CloudFlare R2 Storage Settings
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "virallab-media"
    r2_public_url: str = ""
    storage_mode: str = "local"  # "local" or "r2"

    # Admin settings
    admin_secret_key: str = "change-this-admin-secret-key"  # Change in production!

    # Public URL for generating external links (screenshots, etc.)
    # Set this to your public domain/IP in production
    public_base_url: Optional[str] = None  # e.g., "https://yourdomain.com" or "http://35.226.2.144:8888"
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }
    
    @property
    def r2_endpoint_url(self) -> str:
        """CloudFlare R2 S3-compatible endpoint URL."""
        return f"https://{self.r2_account_id}.r2.cloudflarestorage.com"
    
    @property
    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key or os.getenv("OPENAI_API_KEY"))
    
    @property
    def has_gemini_key(self) -> bool:
        return bool(
            self.gemini_api_key or 
            self.google_api_key or 
            os.getenv("GEMINI_API_KEY") or 
            os.getenv("GOOGLE_API_KEY")
        )


# Directory Setup
BASE_DIR = Path(__file__).parent.parent.parent
USER_DATA_DIR = BASE_DIR / "user_data"
FACE_DIR = USER_DATA_DIR / "faces"
AUDIO_DIR = USER_DATA_DIR / "audio"
THUMBNAILS_DIR = BASE_DIR / "generated_thumbnails"
FRONTEND_DIR = BASE_DIR / "frontend" / "dist"

# Ensure directories exist
USER_DATA_DIR.mkdir(exist_ok=True)
FACE_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)
THUMBNAILS_DIR.mkdir(exist_ok=True)

# Global settings instance
settings = Settings()

