from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # MongoDB
    mongodb_url: str
    database_name: str
    
    # Groq
    groq_api_key: str
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS
    frontend_url: str
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()