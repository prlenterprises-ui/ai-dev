"""
Portal Python - Unified Backend for AI Dev Portal

This is the main entry point that combines:
- GraphQL API (via Strawberry)
- REST endpoints (for specific use cases)
- AI/LLM integrations

Run with: uv run python main.py
Or: uv run uvicorn main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from apis.graphql_schema import schema
from apis.rest_routes import router as rest_router
from python.config import settings
from python.error_handlers import register_error_handlers
from python.logging_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - runs on startup and shutdown."""
    # Startup
    logger.info("Starting AI Dev Portal API", extra={
        "environment": settings.environment,
        "port": settings.port,
    })
    
    # Create necessary directories
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
    
    logger.info("Directories initialized", extra={
        "upload_dir": settings.upload_dir,
        "output_dir": settings.output_dir,
    })
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Dev Portal API")


# Create FastAPI app
app = FastAPI(
    title="AI Dev Portal API",
    description="Unified backend combining resume tools, LLM council, and job automation",
    version="0.1.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)

# Register error handlers
register_error_handlers(app)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list if not settings.is_production else settings.cors_origins_list,
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
    """Health check endpoint for monitoring."""
    import sys
    
    health_status = {
        "status": "healthy",
        "environment": settings.environment,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "services": {
            "api": "up",
            "graphql": "up",
        },
        "config": {
            "has_openrouter_key": bool(settings.openrouter_api_key),
            "has_openai_key": bool(settings.openai_api_key),
            "has_anthropic_key": bool(settings.anthropic_api_key),
        }
    }
    
    return health_status


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload and settings.is_development,
        log_level=settings.log_level.lower(),
    )

