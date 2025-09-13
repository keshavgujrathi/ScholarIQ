from pydantic import AnyHttpUrl, validator, Field
from pydantic_settings import BaseSettings
from typing import List, Optional, Union, Dict, Any
import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "ScholarIQ"
    APP_ENV: str = "development"  # development, staging, production
    DEBUG: bool = True
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = "sqlite:///./scholariq.db"
    TEST_DATABASE_URL: str = "sqlite:///./test_scholariq.db"
    
    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT: str = "json"  # json, text
    LOG_FILE: Optional[str] = "logs/app.log"
    
    # File Uploads
    UPLOAD_DIR: str = "data/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "application/pdf"]
    
    # API Keys (add your API keys here)
    OPENAI_API_KEY: Optional[str] = None
    
    # CORS Configuration
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database URL validation
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        
        # Handle SQLite
        if values.get("APP_ENV") == "test":
            return values.get("TEST_DATABASE_URL", "sqlite:///./test_scholariq.db")
        return "sqlite:///./scholariq.db"
    
    # Ensure upload directory exists
    @validator("UPLOAD_DIR", pre=True)
    def ensure_upload_dir_exists(cls, v: str) -> str:
        path = Path(v)
        if not path.is_absolute():
            path = Path(__file__).parent.parent.parent / v
        path.mkdir(parents=True, exist_ok=True)
        return str(path)
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env file

# Create settings instance
settings = Settings()

# Create necessary directories
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
if settings.LOG_FILE:
    Path(settings.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
