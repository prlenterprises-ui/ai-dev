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
    job_title: str = Field(index=True)
    company: str = Field(index=True)
    job_description: Optional[str] = None
    job_url: Optional[str] = None

    status: str = Field(default="pending", index=True)  # pending, in_progress, completed, failed

    resume_url: Optional[str] = None
    cover_letter_url: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.now, index=True)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Metadata
    notes: Optional[str] = None
    match_score: Optional[float] = None


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
