"""
Monitoring and observability utilities for production.
Includes Prometheus metrics and structured logging.
"""

import logging
import time
from functools import wraps
from typing import Any, Callable

from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


# =============================================================================
# Prometheus Metrics
# =============================================================================

# Request metrics
http_requests_total = Counter(
    "http_requests_total", "Total number of HTTP requests", ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds", "HTTP request latency in seconds", ["method", "endpoint"]
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress", "Number of HTTP requests in progress", ["method", "endpoint"]
)

# LLM metrics
llm_requests_total = Counter(
    "llm_requests_total", "Total number of LLM API requests", ["provider", "model", "status"]
)

llm_request_duration_seconds = Histogram(
    "llm_request_duration_seconds", "LLM API request latency in seconds", ["provider", "model"]
)

llm_tokens_used = Counter(
    "llm_tokens_used_total",
    "Total number of tokens used by LLMs",
    ["provider", "model", "type"],  # type: input/output
)

# Database metrics
db_queries_total = Counter(
    "db_queries_total", "Total number of database queries", ["operation", "table", "status"]
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds", "Database query latency in seconds", ["operation", "table"]
)

db_connections_active = Gauge("db_connections_active", "Number of active database connections")

# File upload metrics
file_uploads_total = Counter(
    "file_uploads_total", "Total number of file uploads", ["file_type", "status"]
)

file_upload_size_bytes = Histogram(
    "file_upload_size_bytes", "Size of uploaded files in bytes", ["file_type"]
)

# Rate limiting metrics
rate_limit_exceeded_total = Counter(
    "rate_limit_exceeded_total", "Number of requests blocked by rate limiting", ["ip_address"]
)


# =============================================================================
# Middleware for Request Metrics
# =============================================================================


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP request metrics."""

    async def dispatch(self, request: Request, call_next):
        """Record metrics for each request."""
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        endpoint = request.url.path

        # Track in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        # Measure request duration
        start_time = time.time()

        try:
            response = await call_next(request)
            status = response.status_code

            # Record successful request
            duration = time.time() - start_time
            http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
            http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

            return response

        except Exception:
            # Record failed request
            duration = time.time() - start_time
            http_requests_total.labels(method=method, endpoint=endpoint, status=500).inc()
            http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
            raise

        finally:
            # Decrement in-progress counter
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()


# =============================================================================
# Decorators for Function Metrics
# =============================================================================


def track_llm_request(provider: str, model: str):
    """Decorator to track LLM API requests."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            status = "success"

            try:
                result = await func(*args, **kwargs)

                # Track tokens if available in result
                if isinstance(result, dict):
                    if "input_tokens" in result:
                        llm_tokens_used.labels(provider=provider, model=model, type="input").inc(
                            result["input_tokens"]
                        )

                    if "output_tokens" in result:
                        llm_tokens_used.labels(provider=provider, model=model, type="output").inc(
                            result["output_tokens"]
                        )

                return result

            except Exception:
                status = "error"
                raise

            finally:
                duration = time.time() - start_time
                llm_requests_total.labels(provider=provider, model=model, status=status).inc()
                llm_request_duration_seconds.labels(provider=provider, model=model).observe(
                    duration
                )

        return wrapper

    return decorator


def track_db_query(operation: str, table: str):
    """Decorator to track database queries."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            status = "success"

            try:
                result = await func(*args, **kwargs)
                return result

            except Exception:
                status = "error"
                raise

            finally:
                duration = time.time() - start_time
                db_queries_total.labels(operation=operation, table=table, status=status).inc()
                db_query_duration_seconds.labels(operation=operation, table=table).observe(duration)

        return wrapper

    return decorator


# =============================================================================
# Metrics Endpoint
# =============================================================================


def get_metrics() -> Response:
    """Return Prometheus metrics in text format."""
    metrics_data = generate_latest()
    return Response(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST,
    )


# =============================================================================
# Health Check with Metrics
# =============================================================================


async def get_health_with_metrics() -> dict:
    """
    Health check endpoint that includes basic metrics.

    Returns:
        dict: Health status with request counts and latencies
    """
    from python.database import engine

    # Database connection check
    db_healthy = False
    try:
        async with engine.connect():
            db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")

    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "disconnected",
        "timestamp": time.time(),
        "metrics": {
            "requests_total": (
                http_requests_total._value.get() if hasattr(http_requests_total, "_value") else 0
            ),
            "requests_in_progress": (
                http_requests_in_progress._value.get()
                if hasattr(http_requests_in_progress, "_value")
                else 0
            ),
            "db_connections_active": (
                db_connections_active._value.get()
                if hasattr(db_connections_active, "_value")
                else 0
            ),
        },
    }


# =============================================================================
# Logging Utilities
# =============================================================================


class StructuredLogger:
    """Structured logging helper for consistent log formatting."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_request(
        self, method: str, path: str, status: int, duration_ms: float, user_id: str = None, **extra
    ):
        """Log HTTP request with structured data."""
        self.logger.info(
            "HTTP request",
            extra={
                "method": method,
                "path": path,
                "status": status,
                "duration_ms": duration_ms,
                "user_id": user_id,
                **extra,
            },
        )

    def log_llm_call(
        self,
        provider: str,
        model: str,
        duration_ms: float,
        tokens_used: int = None,
        status: str = "success",
        **extra,
    ):
        """Log LLM API call with structured data."""
        self.logger.info(
            "LLM API call",
            extra={
                "provider": provider,
                "model": model,
                "duration_ms": duration_ms,
                "tokens_used": tokens_used,
                "status": status,
                **extra,
            },
        )

    def log_db_query(
        self, operation: str, table: str, duration_ms: float, rows_affected: int = None, **extra
    ):
        """Log database query with structured data."""
        self.logger.info(
            "Database query",
            extra={
                "operation": operation,
                "table": table,
                "duration_ms": duration_ms,
                "rows_affected": rows_affected,
                **extra,
            },
        )

    def log_error(self, error: Exception, context: dict = None, **extra):
        """Log error with structured context."""
        self.logger.error(
            f"Error: {str(error)}",
            extra={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context or {},
                **extra,
            },
            exc_info=True,
        )
