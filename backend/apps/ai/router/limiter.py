
"""Rate limiter for user requests using Redis."""
from .client import RedisRouterClient


class RateLimiter:
    """Limits the number of requests a user can make within a time window."""
    def __init__(self):
        """Initialize RateLimiter with Redis connection, limit, and window."""
        self.redis = RedisRouterClient().get_connection()
        self.limit = 20  # Max requests
        self.window = 60  # Time window in seconds

    def is_allowed(self, user_id: str) -> bool:
        """Return True if user is within limits, False if blocked."""
        # RFC 4.2: Scoped Key
        key = f"nestbot_cache:rate_limit:{user_id}"

        try:
            # 1. Increment counter atomically
            current_count = self.redis.incr(key)

            # 2. Set an expiry on first request
            if current_count == 1:
                self.redis.expire(key, self.window)

            # 3. Check limit
            return not current_count > self.limit

        except Exception:
            # RFC 3.1.3: Fail-Open
            # If Redis is down, do NOT block the user. Allow traffic.
            return True
