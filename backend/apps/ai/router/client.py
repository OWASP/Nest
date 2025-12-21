"""Redis client for router operations with fail-open policy."""

import logging
import os

import redis
from dotenv import load_dotenv

# Load secrets from .env file
load_dotenv()

# RFC 3.1.3: Fail-Open Policy Configuration
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", "6379") or "6379"),
    "username": os.getenv("REDIS_USER", "nest_router"),
    "password": os.getenv("REDIS_PASSWORD"),
    "decode_responses": True,
    # Strict 50ms timeout. If Redis is slow, we drop the connection.
    "socket_timeout": 0.05,
    "socket_connect_timeout": 0.05,
}

logger = logging.getLogger(__name__)


class RedisRouterClient:
    """Redis client wrapper with singleton connection pool and fail-open policy."""

    _pool = None

    def __init__(self):
        """Initialize Redis client with singleton connection pool."""
        # RFC 3.1.1: Singleton BlockingConnectionPool
        if not RedisRouterClient._pool:
            if not REDIS_CONFIG["password"]:
                logger.warning("⚠️ REDIS_PASSWORD is missing in .env")

            try:
                RedisRouterClient._pool = redis.BlockingConnectionPool(
                    **REDIS_CONFIG, max_connections=10
                )
            except Exception:
                logger.exception("Failed to create Redis pool")
                raise

        self.client = redis.Redis(connection_pool=RedisRouterClient._pool)

    def get_connection(self):
        """Return the Redis client instance.

        Operations on this client might raise TimeoutError (Circuit Breaker).
        """
        return self.client
