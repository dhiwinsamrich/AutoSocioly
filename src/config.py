from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # GetLate API Configuration
    GETLATE_API_KEY: str
    GETLATE_BASE_URL: str = "https://getlate.dev/api/v1"
    
    # Google Gemini AI Configuration
    GOOGLE_API_KEY: str
    GEMINI_MODEL_ID: str = "gemini-2.0-flash-001"
    GEMINI_IMAGE_MODEL_ID: str = "gemini-2.5-flash-image-preview"
    
    # Additional AI Configuration (from .env file)
    LATE_API_KEY: Optional[str] = None
    IMAGE_MODEL_ID: Optional[str] = None
    TEXT_MODEL_ID: Optional[str] = None
    
    # Application Configuration
    SECRET_KEY: str = "your-secret-key-change-this"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    BASE_URL: str = "http://localhost:8000"
    
    # File Upload Configuration
    UPLOAD_FOLDER: str = "static/uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS: set = {"png", "jpg", "jpeg", "gif", "webp"}
    
    # Ngrok Configuration (Optional)
    NGROK_AUTHTOKEN: Optional[str] = None
    USE_NGROK: bool = False
    
    # Redis Configuration (Optional - for future caching)
    REDIS_URL: Optional[str] = None
    
    # Security Configuration
    RATE_LIMIT_PER_MINUTE: int = 60
    SESSION_COOKIE_SECURE: bool = False
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "lax"
    
    # Social Media Platform Settings
    SUPPORTED_PLATFORMS: list = [
        "facebook", "instagram", "linkedin", "x", "twitter", 
        "reddit", "pinterest", "tiktok", "youtube"
    ]
    
    # Content Generation Settings
    DEFAULT_TONE: str = "engaging"
    DEFAULT_CAPTION_LENGTH: str = "medium"
    DEFAULT_HASHTAG_COUNT: int = 10
    MAX_HASHTAG_COUNT: int = 30
    MIN_HASHTAG_COUNT: int = 1
    
    # Image Generation Settings
    IMAGE_GENERATION_TIMEOUT: int = 60  # seconds
    IMAGE_QUALITY: str = "high"
    MAX_IMAGE_SIZE: int = 2048  # pixels
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)