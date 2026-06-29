import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "SplashDevAgent"
    DEBUG: bool = True
    JWT_SECRET: str = "your-jwt-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    MONGODB_URI: str = "mongodb://localhost:27017/splash_dev_agent"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # LLM Settings
    LLM_PROVIDER: str = "openai"  # "openai" or "anthropic"
    OPENAI_API_KEY: Optional[str] = ""
    ANTHROPIC_API_KEY: Optional[str] = ""
    
    # Agent Custom Configs
    DEV_CACHE_TTL: int = 3600
    DEV_TIMEOUT_SECONDS: int = 120
    
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
