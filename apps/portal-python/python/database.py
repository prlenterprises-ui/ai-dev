"""
Database models and connection management.

Using SQLModel for async SQLAlchemy with Pydantic integration.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Field, SQLModel

from .config import settings

# =============================================================================
# MODELS
# =============================================================================


class JobApplication(SQLModel, table=True):
    """Job application tracking."""

    __tablename__ = "job_applications"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Basic fields for indexing/search (extracted from JSON for convenience)
    job_title: str = Field(index=True)
    company: str = Field(index=True)
    job_url: Optional[str] = None
    source: Optional[str] = None  # Job board source (jsearch-linkedin, jsearch-indeed, etc.)
    
    status: str = Field(default="pending", index=True)  # pending, in_progress, completed, failed

    resume_url: Optional[str] = None
    cover_letter_url: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.now, index=True)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Metadata
    notes: Optional[str] = None
    match_score: Optional[float] = None
    
    # SOURCE OF TRUTH: Complete JSearch API responses (stored as JSON text)
    # These contain ALL data returned by JSearch - use these as primary data source
    jsearch_search_response: Optional[str] = None  # Complete job object from /search endpoint (PRIMARY)
    jsearch_details_response: Optional[str] = None  # Complete response from /job-details endpoint (optional)
    jsearch_salary_response: Optional[str] = None  # Complete response from /estimated-salary endpoint (optional)
    
    # Deprecated fields - kept for backward compatibility, data is in jsearch_search_response
    job_description: Optional[str] = None  # Use jsearch_search_response instead
    
    def get_jsearch_data(self) -> Optional[dict]:
        """Parse and return the complete JSearch job data (source of truth)."""
        if self.jsearch_search_response:
            import json
            try:
                return json.loads(self.jsearch_search_response)
            except json.JSONDecodeError:
                return None
        return None
    
    def get_full_description(self) -> Optional[str]:
        """Get complete job description from JSearch data."""
        data = self.get_jsearch_data()
        return data.get("job_description") if data else self.job_description
    
    def get_salary_info(self) -> Optional[dict]:
        """Get salary information from JSearch data."""
        data = self.get_jsearch_data()
        if data:
            return {
                "min": data.get("job_min_salary"),
                "max": data.get("job_max_salary"),
                "currency": data.get("job_salary_currency"),
                "period": data.get("job_salary_period")
            }
        return None
    
    def get_location_details(self) -> Optional[dict]:
        """Get detailed location info from JSearch data."""
        data = self.get_jsearch_data()
        if data:
            return {
                "city": data.get("job_city"),
                "state": data.get("job_state"),
                "country": data.get("job_country"),
                "is_remote": data.get("job_is_remote"),
                "latitude": data.get("job_latitude"),
                "longitude": data.get("job_longitude")
            }
        return None


class ResumeVersion(SQLModel, table=True):
    """Resume version tracking."""

    __tablename__ = "resume_versions"

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    file_path: str
    content_type: str
    size: int

    # Extracted content
    text_content: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.now, index=True)

    # Link to application if tailored
    application_id: Optional[int] = Field(default=None, foreign_key="job_applications.id")


class CouncilQuery(SQLModel, table=True):
    """LLM Council query history."""

    __tablename__ = "council_queries"

    id: Optional[int] = Field(default=None, primary_key=True)
    query: str
    final_answer: str

    # Metadata
    models_used: str  # JSON array of model names
    total_tokens: int = 0
    total_latency_ms: float = 0

    created_at: datetime = Field(default_factory=datetime.now, index=True)


class Config(SQLModel, table=True):
    """Application configuration storage."""

    __tablename__ = "configs"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # e.g., "auto_apply", "matching_service"
    title: str  # Display name
    description: Optional[str] = None
    config_json: str  # JSON string of configuration
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# =============================================================================
# DATABASE CONNECTION
# =============================================================================


def get_database_url() -> str:
    """Get database URL based on environment."""
    if settings.database_url:
        url = settings.database_url
        # Ensure async SQLite driver
        if url.startswith("sqlite:") and not url.startswith("sqlite+aiosqlite:"):
            url = url.replace("sqlite:", "sqlite+aiosqlite:")
        return url

    # Default to async SQLite for development
    return "sqlite+aiosqlite:///./portal.db"


# Create async engine
engine = create_async_engine(
    get_database_url(),
    echo=settings.is_development,
    future=True,
)

# Create session factory
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """Dependency for getting database sessions."""
    async with async_session_maker() as session:
        yield session


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db():
    """Close database connections."""
    await engine.dispose()
