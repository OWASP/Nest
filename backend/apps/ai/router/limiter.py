"""Rate limiter for user requests using Redis."""

import hashlib

from .client import RedisRouterClient

RATE_LIMIT_SCRIPT = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return count
"""

RATE_LIMIT_SCRIPT_SHA = hashlib.sha256(RATE_LIMIT_SCRIPT.encode()).hexdigest()


class RateLimiter:
    """Limits the number of requests a user can make within a time window."""

    def __init__(self):
        """Initialize RateLimiter with Redis connection, limit, and window."""
        self.redis = RedisRouterClient().get_connection()
        self.limit = 20
        self.window = 60
        self._script_sha = None

    def _get_script_sha(self):
        """Get or load the Lua script SHA for EVALSHA."""
        if self._script_sha is None:
            try:
                self._script_sha = self.redis.script_load(RATE_LIMIT_SCRIPT)
            except (AttributeError, ValueError, TypeError, RuntimeError):
                # Log the exception if needed
                self._script_sha = RATE_LIMIT_SCRIPT_SHA
        return self._script_sha

    def _increment_with_expiry(self, key: str, window: int) -> int:
        """Atomically increment counter and set expiry using Lua script.

        Returns the counter value after increment.
        """
        script_sha = self._get_script_sha()
        try:
            current_count = self.redis.evalsha(script_sha, 1, key, window)
        except (AttributeError, ValueError, TypeError, RuntimeError) as e:
            error_str = str(e).lower()
            if "noscript" in error_str or "unknown script" in error_str:
                try:
                    current_count = self.redis.eval(RATE_LIMIT_SCRIPT, 1, key, window)
                    self._script_sha = self.redis.script_load(RATE_LIMIT_SCRIPT)
                except (AttributeError, ValueError, TypeError, RuntimeError):
                    # Log the exception if needed
                    return 0
            else:
                return 0
        return int(current_count) if current_count is not None else 0

    def is_allowed(self, user_id: str) -> bool:
        """Return True if user is within limits, False if blocked."""
        key = f"nestbot_cache:rate_limit:{user_id}"

        try:
            current_count = self._increment_with_expiry(key, self.window)
        except Exception:  # noqa: BLE001 - Intentional fail-open policy
            return True
        else:
            return current_count <= self.limit
