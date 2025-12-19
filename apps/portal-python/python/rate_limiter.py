"""
Rate limiting middleware for API protection.
Prevents abuse and DoS attacks with configurable limits.
"""

import logging
import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RateLimiter(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm.

    Tracks requests per IP address and enforces configurable limits.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10,
    ):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI application instance
            requests_per_minute: Max requests per minute per IP
            requests_per_hour: Max requests per hour per IP
            burst_size: Max requests in rapid succession (within 1 second)
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size

        # Storage: {ip_address: [(timestamp, count), ...]}
        self.request_history: Dict[str, list] = defaultdict(list)

        # Cleanup interval to prevent memory bloat
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, considering proxy headers."""
        # Check for proxy headers first
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client
        if request.client:
            return request.client.host

        return "unknown"

    def _cleanup_old_entries(self):
        """Remove old entries to prevent memory bloat."""
        now = time.time()

        # Only cleanup periodically
        if now - self.last_cleanup < self.cleanup_interval:
            return

        cutoff_time = now - 3600  # Keep last hour

        for ip in list(self.request_history.keys()):
            # Filter out old entries
            self.request_history[ip] = [
                (ts, count) for ts, count in self.request_history[ip] if ts > cutoff_time
            ]

            # Remove IP if no recent requests
            if not self.request_history[ip]:
                del self.request_history[ip]

        self.last_cleanup = now
        logger.debug(f"Cleaned up rate limiter, tracking {len(self.request_history)} IPs")

    def _check_rate_limit(self, ip: str) -> Tuple[bool, str, int]:
        """
        Check if request should be allowed.

        Returns:
            Tuple of (allowed, error_message, retry_after_seconds)
        """
        now = time.time()
        history = self.request_history[ip]

        # Add current request
        history.append((now, 1))

        # Check burst limit (within 1 second)
        burst_count = sum(count for ts, count in history if now - ts <= 1)
        if burst_count > self.burst_size:
            return False, "Too many requests in rapid succession", 1

        # Check per-minute limit
        minute_count = sum(count for ts, count in history if now - ts <= 60)
        if minute_count > self.requests_per_minute:
            return False, "Rate limit exceeded (per minute)", 60

        # Check per-hour limit
        hour_count = sum(count for ts, count in history if now - ts <= 3600)
        if hour_count > self.requests_per_hour:
            return False, "Rate limit exceeded (per hour)", 3600

        return True, "", 0

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for health checks and test client
        if (
            request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json", "/metrics"]
            or self._get_client_ip(request) == "testclient"
        ):
            return await call_next(request)

        # Periodic cleanup
        self._cleanup_old_entries()

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Check rate limit
        allowed, error_msg, retry_after = self._check_rate_limit(client_ip)

        if not allowed:
            logger.warning(f"Rate limit exceeded for {client_ip}: {error_msg}")

            # Return 429 Too Many Requests
            return Response(
                content=f'{{"detail": "{error_msg}"}}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + retry_after)),
                    "Content-Type": "application/json",
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        minute_count = sum(
            count for ts, count in self.request_history[client_ip] if time.time() - ts <= 60
        )
        remaining = max(0, self.requests_per_minute - minute_count)

        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))

        return response


# Default rate limiter instance with reasonable limits
def create_rate_limiter(
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000,
    burst_size: int = 10,
) -> RateLimiter:
    """
    Create a rate limiter with custom settings.

    Default limits:
    - 60 requests per minute
    - 1000 requests per hour
    - 10 requests burst within 1 second

    Adjust based on your API usage patterns.
    """
    from fastapi import FastAPI

    app = FastAPI()  # Placeholder, will be replaced by middleware setup

    return RateLimiter(
        app=app,
        requests_per_minute=requests_per_minute,
        requests_per_hour=requests_per_hour,
        burst_size=burst_size,
    )
