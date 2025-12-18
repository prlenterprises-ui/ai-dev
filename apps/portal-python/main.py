"""
Portal Python - Unified Backend for AI Dev Portal

This is the main entry point that combines:
- GraphQL API (via Strawberry)
- REST endpoints (for specific use cases)
- AI/LLM integrations

Run with: uv run python main.py
Or: uv run uvicorn main:app --reload --port 8000
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from apis.graphql_schema import schema
from apis.rest_routes import router as rest_router

# Create FastAPI app
app = FastAPI(
    title="AI Dev Portal API",
    description="Unified backend combining resume tools, LLM council, and job automation",
    version="0.1.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
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
        "endpoints": {
            "graphql": "/graphql",
            "graphql_playground": "/graphql",
            "rest_api": "/api",
            "health": "/api/health",
        },
        "modules": [
            "jobbernaut-tailor",
            "aihawk",
            "llm-council",
            "resume-lm",
            "resume-matcher",
        ],
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

