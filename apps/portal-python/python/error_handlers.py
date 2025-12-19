"""
Error handling middleware and exception handlers.

Provides consistent error responses and logging across the application.
"""

import traceback
from typing import Any, Dict

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from python.logging_config import logger


class APIError(Exception):
    """Base exception for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Dict[str, Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation error."""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class NotFoundError(APIError):
    """Resource not found error."""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class AuthenticationError(APIError):
    """Authentication error."""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)


class ServiceUnavailableError(APIError):
    """External service unavailable error."""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, details)


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle APIError exceptions."""
    logger.error(
        f"API Error: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "details": exc.details,
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "details": exc.details,
                "path": request.url.path,
            }
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPException."""
    logger.warning(
        f"HTTP Exception: {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": str(exc.detail),
                "path": request.url.path,
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    # Log full traceback for debugging
    tb = traceback.format_exc()
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": tb,
        }
    )

    # Return generic error to client (don't leak internal details)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "An unexpected error occurred",
                "path": request.url.path,
            }
        },
    )


def register_error_handlers(app) -> None:
    """Register all error handlers with the FastAPI app."""
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
