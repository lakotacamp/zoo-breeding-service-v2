# app/settings.py

import logging
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Global application settings."""
    COOL_DOWN_DAYS: int = 180  # from your original code
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Zoo Breeding Service API"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/zoo"


    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


# Initialize logging or other global config
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

settings = Settings()
