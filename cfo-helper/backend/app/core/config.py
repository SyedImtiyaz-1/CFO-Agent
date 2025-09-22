from pydantic import BaseSettings, Field
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CFO Helper API"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # GROQ API Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["text/plain", "application/pdf", "text/csv", 
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]
    
    # RAG Settings
    VECTOR_STORE_DIMENSION: int = 384
    SIMILARITY_TOP_K: int = 3
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Create settings instance
settings = Settings()

# Update CORS origins with any additional origins from environment
if os.getenv("FRONTEND_URL"):
    settings.BACKEND_CORS_ORIGINS.append(os.getenv("FRONTEND_URL"))
