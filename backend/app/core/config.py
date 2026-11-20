"""Core application configuration using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable override support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Q-TRACE"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    HOST: str = "127.0.0.1"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = "sqlite:///./qtrace.db"
    STORAGE_ROOT: str = "./storage"

    MAX_UPLOAD_BYTES: int = 50 * 1024 * 1024  # 50 MB
    MAX_IMAGE_WIDTH: int = 8192
    MAX_IMAGE_HEIGHT: int = 8192
    ALLOWED_IMAGE_EXTENSIONS: List[str] = Field(
        default_factory=lambda: ["jpg", "jpeg", "png", "tif", "tiff"]
    )
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )

    @property
    def storage_path(self) -> Path:
        """Return absolute Path object for the storage root directory."""
        return Path(self.STORAGE_ROOT).resolve()


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()

