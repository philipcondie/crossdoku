from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Pydantic's BaseSettings automatically reads from:
    1. Environment variables
    2. .env file (if python-dotenv is installed)
    """

    database_url: str = "sqlite:///database.db"
    cors_origins: str = "http://localhost:5173"
    environment: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # This makes CORS_ORIGINS in .env map to cors_origins in Python
        env_prefix = ""


@lru_cache
def get_settings() -> Settings:
    """
    Returns cached settings instance.

    @lru_cache ensures we only load from env/file once,
    not on every import or function call.
    """
    return Settings()
