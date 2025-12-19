"""
Configuration management using Pydantic Settings.

Environment variables are loaded from .env file and validated.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field
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
    environment: str = Field(
        default="development",
        description="Environment: development, staging, production",
    )
    debug: bool = True
    reload: bool = True

    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated list of allowed origins"
    )

    # Database (future)
    database_url: str = "sqlite:///./portal.db"

    # Storage
    upload_dir: str = Field(default="/tmp/uploads", description="Upload directory")
    max_upload_size: int = Field(default=10485760, description="Max upload size in bytes (10MB)")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")

    # LLM Council Config
    council_models: str = (
        "openai/gpt-4o,anthropic/claude-3-5-sonnet,"
        "anthropic/claude-3-5-haiku,google/gemini-2.0-flash-exp"
    )
    chairman_model: str = "google/gemini-2.0-flash-thinking-exp"
    council_timeout: int = Field(default=120, description="Council timeout in seconds")
    council_max_retries: int = Field(default=3, description="Council max retries")

    # Ollama Config (for local models)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Security
    api_key_header: str = Field(default="X-API-Key", description="API key header name")
    api_key: Optional[str] = Field(default=None, description="API key for securing endpoints")

    # Feature Flags
    enable_council: bool = Field(default=True, description="Enable LLM Council")
    enable_resume_matching: bool = Field(default=True, description="Enable resume matching")
    enable_jobbernaut: bool = Field(default=True, description="Enable Jobbernaut")
    enable_file_uploads: bool = Field(default=True, description="Enable file uploads")

    # Output directories
    output_dir: str = "./outputs"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() == "development"

    def get_council_models_list(self) -> list[str]:
        """Parse council_models string into list."""
        return [m.strip() for m in self.council_models.split(",") if m.strip()]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Create global settings instance
settings = get_settings()
