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

    # CORS — comma-separated origins
    # Dev:  http://localhost:5173,http://localhost:5174
    # Prod: https://yourdomain.com
    frontend_url: str = "http://localhost:5173"
    allowed_origins: str = "http://localhost:5173,http://localhost:5174"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


# Module-level singleton — import this in main.py and other files
settings = get_settings()