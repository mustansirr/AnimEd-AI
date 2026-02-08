"""
Application configuration using pydantic-settings.
Loads environment variables and provides typed access to settings.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables or .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Supabase Configuration
    supabase_url: str = ""
    supabase_key: str = ""

    # LLM Provider Configuration
    groq_api_key: str = ""
    openrouter_api_key: str = ""
    llm_provider: Literal["groq", "openrouter"] = "groq"

    # Storage Configuration
    storage_path: str = "./storage"  # Local path for video files
    storage_bucket: str = "video-segments"  # Supabase Storage bucket

    # Application Settings
    debug: bool = False

    @property
    def is_supabase_configured(self) -> bool:
        """Check if Supabase credentials are configured."""
        return bool(self.supabase_url and self.supabase_key)

    @property
    def is_llm_configured(self) -> bool:
        """Check if at least one LLM provider is configured."""
        if self.llm_provider == "groq":
            return bool(self.groq_api_key)
        return bool(self.openrouter_api_key)


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings getter.

    Returns the same Settings instance for the lifetime of the application,
    avoiding repeated environment variable parsing.
    """
    return Settings()
