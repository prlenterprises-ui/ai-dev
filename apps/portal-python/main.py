"""
Portal Python - Unified Backend for AI Dev Portal

This is the main entry point that combines:
- GraphQL API (via Strawberry)
- REST endpoints (for specific use cases)
- AI/LLM integrations

Run with: uv run python main.py
Or: uv run uvicorn main:app --reload --port 8000
"""

from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from apis.graphql_schema import schema
from apis.rest_routes import router as rest_router
from python.config import settings
from python.database import close_db, init_db
from python.error_handlers import register_error_handlers
from python.logging_config import logger
from python.monitoring import MetricsMiddleware, get_health_with_metrics, get_metrics
from python.rate_limiter import RateLimiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - runs on startup and shutdown."""
    # Startup
    logger.info(
        "Starting AI Dev Portal API",
        extra={
            "environment": settings.environment,
            "port": settings.port,
        },
    )

    # Create necessary directories
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)

    logger.info(
        "Directories initialized",
        extra={
            "upload_dir": settings.upload_dir,
            "output_dir": settings.output_dir,
        },
    )

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    yield

    # Shutdown
    logger.info("Shutting down AI Dev Portal API")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="AI Dev Portal API",
    description="""
    Unified backend for AI-powered career development tools.

    ## Features

    * **LLM Council**: Multi-model deliberation system using GPT-4, Claude, Gemini, and Llama
    * **Resume Matching**: AI-powered resume analysis and job matching
    * **Job Applications**: Automated application tracking and tailoring
    * **File Uploads**: Support for resumes and job descriptions (PDF, DOCX, TXT)

    ## GraphQL Playground

    Visit `/graphql` for the interactive GraphQL IDE.

    ## REST Endpoints

    Traditional REST APIs for file uploads and real-time events.
    """,
    version="0.1.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check and monitoring endpoints",
        },
        {
            "name": "uploads",
            "description": "File upload endpoints for resumes and job descriptions",
        },
        {
            "name": "events",
            "description": "Server-sent events for real-time updates",
        },
    ],
    lifespan=lifespan,
)

# Register error handlers
register_error_handlers(app)

# Add monitoring middleware
app.add_middleware(MetricsMiddleware)

# Add rate limiting middleware
app.add_middleware(
    RateLimiter,
    requests_per_minute=60,
    requests_per_hour=1000,
    burst_size=10,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        settings.cors_origins_list if not settings.is_production else settings.cors_origins_list
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount GraphQL endpoint
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# Mount REST routes (for specific endpoints that work better as REST)
app.include_router(rest_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Dev Portal API",
        "version": "0.1.0",
        "environment": settings.environment,
        "endpoints": {
            "graphql": "/graphql",
            "graphql_playground": "/graphql",
            "rest_api": "/api",
            "health": "/api/health",
            "docs": "/docs" if settings.is_development else None,
        },
        "modules": [
            "jobbernaut-tailor",
            "aihawk",
            "llm-council",
            "resume-lm",
            "resume-matcher",
        ],
        "features": {
            "council": settings.enable_council,
            "resume_matching": settings.enable_resume_matching,
            "jobbernaut": settings.enable_jobbernaut,
            "file_uploads": settings.enable_file_uploads,
        },
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns detailed health status including database connectivity.
    """
    return await get_health_with_metrics()


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.
    Returns metrics in Prometheus text format.
    """
    return get_metrics()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload and settings.is_development,
        log_level=settings.log_level.lower(),
    )
