"""
Rate Limiting Middleware
Redis-based rate limiting with tier-based limits
"""

from typing import Optional, Callable
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis.asyncio as redis
import time
import structlog

from app.core.config import settings
from app.models.user import UserTier

logger = structlog.get_logger()

# Rate limits by tier (requests per minute)
TIER_LIMITS = {
    UserTier.STARTER: 60,
    UserTier.GROWTH: 300,
    UserTier.GOD_MODE: 1000,
    "anonymous": 30,
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis sliding window.
    """
    
    def __init__(self, app, redis_url: str = None):
        super().__init__(app)
        self.redis_url = redis_url or settings.redis_url
        self.redis: Optional[redis.Redis] = None
    
    async def get_redis(self) -> redis.Redis:
        """Get or create Redis connection"""
        if self.redis is None:
            self.redis = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self.redis
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/api/v1/health", "/", "/api/v1/docs"]:
            return await call_next(request)
        
        # Get identifier (user_id or IP)
        identifier = self._get_identifier(request)
        tier = self._get_tier(request)
        limit = TIER_LIMITS.get(tier, TIER_LIMITS["anonymous"])
        
        # Check rate limit
        try:
            redis_client = await self.get_redis()
            allowed, remaining, reset_at = await self._check_rate_limit(
                redis_client, identifier, limit
            )
        except Exception as e:
            logger.warning("Rate limit check failed", error=str(e))
            # Allow request if Redis fails
            return await call_next(request)
        
        if not allowed:
            return Response(
                content='{"error": "Rate limit exceeded", "retry_after": ' + str(reset_at) + '}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_at),
                    "Retry-After": str(reset_at - int(time.time())),
                },
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_at)
        
        return response
    
    def _get_identifier(self, request: Request) -> str:
        """Get rate limit identifier from request"""
        # Try to get user ID from auth header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # In production, decode JWT to get user ID
            # For now, use the token hash
            import hashlib
            token_hash = hashlib.sha256(auth_header.encode()).hexdigest()[:16]
            return f"user:{token_hash}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def _get_tier(self, request: Request) -> UserTier:
        """Get user tier from request"""
        # In production, decode JWT to get tier
        # For now, return anonymous for IP-based, starter for auth
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return UserTier.STARTER
        return "anonymous"
    
    async def _check_rate_limit(
        self,
        redis_client: redis.Redis,
        identifier: str,
        limit: int,
        window: int = 60,
    ) -> tuple[bool, int, int]:
        """
        Check rate limit using sliding window algorithm.
        
        Returns: (allowed, remaining, reset_timestamp)
        """
        now = int(time.time())
        window_start = now - window
        key = f"ratelimit:{identifier}"
        
        # Use pipeline for atomic operations
        pipe = redis_client.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(now): now})
        
        # Set expiry
        pipe.expire(key, window)
        
        results = await pipe.execute()
        count = results[1]
        
        allowed = count < limit
        remaining = max(0, limit - count - 1)
        reset_at = now + window
        
        return allowed, remaining, reset_at


class CreditCheckMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check credit balance before AI endpoints.
    """
    
    # Endpoints that require credits
    CREDIT_ENDPOINTS = {
        "/api/v1/signals/": 5,
        "/api/v1/growth/leads/generate": 2,
        "/api/v1/growth/content/generate": 3,
        "/api/v1/agents/chat": 1,
        "/api/v1/agents/vision": 20,
        "/api/v1/forge/workflows/run": 10,
    }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if endpoint requires credits
        path = request.url.path
        
        for endpoint, cost in self.CREDIT_ENDPOINTS.items():
            if path.startswith(endpoint) and request.method == "POST":
                # Credit check is handled by RequireCredits dependency
                # This middleware could add additional checks if needed
                break
        
        return await call_next(request)
