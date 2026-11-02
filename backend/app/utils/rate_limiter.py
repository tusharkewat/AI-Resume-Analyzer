import time
import threading
from typing import Dict, List, Optional, Tuple
from fastapi import Request, HTTPException, status
from app.config import settings


class InMemoryRateLimiter:
    """
    Thread-safe sliding-window in-memory rate limiter.
    Limits requests per client within a sliding time window.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._history: Dict[str, List[float]] = {}

    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int = 60) -> Tuple[bool, int]:
        now = time.time()
        with self._lock:
            # Clean up old timestamps
            timestamps = self._history.get(key, [])
            cutoff = now - window_seconds
            timestamps = [t for t in timestamps if t > cutoff]

            if len(timestamps) >= max_requests:
                # Calculate retry-after
                retry_after = max(1, int(timestamps[0] + window_seconds - now))
                self._history[key] = timestamps
                return True, retry_after

            timestamps.append(now)
            self._history[key] = timestamps
            return False, 0

    def reset(self):
        """Resets all tracking history (primarily for testing)."""
        with self._lock:
            self._history.clear()


limiter = InMemoryRateLimiter()


def get_client_identifier(request: Request, user_id: Optional[int] = None) -> str:
    """Extracts client IP or authenticated user ID for rate limiting."""
    if user_id:
        return f"user:{user_id}"
    
    # Check X-Forwarded-For header for reverse proxies
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    elif request.client and request.client.host:
        client_ip = request.client.host
    else:
        client_ip = "unknown_client"
    return f"ip:{client_ip}"


def rate_limit(max_requests: int, window_seconds: int = 60, scope: str = "default"):
    """
    FastAPI dependency generating a rate limiting check.
    """
    async def dependency(request: Request):
        if not settings.RATE_LIMIT_ENABLED:
            return

        client_key = f"{scope}:{get_client_identifier(request)}"
        is_limited, retry_after = limiter.is_rate_limited(
            key=client_key,
            max_requests=max_requests,
            window_seconds=window_seconds
        )

        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds}s. Please retry in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )

    return dependency
