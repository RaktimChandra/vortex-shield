from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri=os.getenv("REDIS_URL", "memory://")
)

# Rate limit configurations
AUTH_RATE_LIMIT = "5/minute"
API_RATE_LIMIT = "60/minute"
CLAIM_RATE_LIMIT = "10/hour"
ANALYTICS_RATE_LIMIT = "30/minute"

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler"""
    return {
        "error": "Rate limit exceeded",
        "detail": f"Too many requests. Please try again later.",
        "retry_after": exc.detail
    }
