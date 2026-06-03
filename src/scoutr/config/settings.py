from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
import functools



class Settings(BaseSettings):
    """Runtime config, read from .env file, see .env_example"""

    model_config = SettingsConfigDict(env_prefix="SCOUTR_", env_file=".env", extra="ignore")


    # Async driver in the scheme is required by SQLAlchemy's async engine.
    database_url: str = "postgresql+asyncpg://scoutr:scoutr@localhost:5432/scoutr"


@functools.cache
def get_settings() -> Settings:
    return Settings()