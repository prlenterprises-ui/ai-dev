"""
Configuration management using Pydantic Settings.

Environment variables are loaded from .env file and validated.
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    google_api_key: Optional[str] = None

    # Server Config
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    reload: bool = True

    # Database (future)
    database_url: Optional[str] = None

    # LLM Council Config
    council_models: str = "openai/gpt-4o,anthropic/claude-3-5-sonnet,google/gemini-2.0-flash-exp"
    chairman_model: str = "google/gemini-2.0-flash-thinking-exp"

    # Ollama Config (for local models)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Output directories
    output_dir: str = "./outputs"

    def get_council_models_list(self) -> list[str]:
        """Parse council_models string into list."""
        return [m.strip() for m in self.council_models.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

