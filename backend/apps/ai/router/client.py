"""Redis client for router operations with fail-open policy."""

import logging
import threading

import redis
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_timeout_value(
    setting_name: str, default: float, min_value: float = 0.1, max_value: float = 5.0
) -> float:
    """Get and validate timeout value from Django settings.

    Args:
        setting_name: Name of the Django setting to retrieve.
        default: Default value if setting is not found or invalid.
        min_value: Minimum allowed timeout value in seconds.
        max_value: Maximum allowed timeout value in seconds.

    Returns:
        Validated timeout value in seconds.

    """
    try:
        timeout = getattr(settings, setting_name, default)
        timeout = float(timeout)
    except (ValueError, TypeError) as e:
        logger.warning(
            "Invalid timeout value for %s: %s. Using default: %s",
            setting_name,
            e,
            default,
        )
        return default

    if timeout < min_value:
        logger.warning(
            "Timeout %s (%s) is below minimum (%s), using minimum value",
            setting_name,
            timeout,
            min_value,
        )
        return min_value

    if timeout > max_value:
        logger.warning(
            "Timeout %s (%s) exceeds maximum (%s), using maximum value",
            setting_name,
            timeout,
            max_value,
        )
        return max_value

    return timeout


class RedisRouterClient:
    """Redis client wrapper with shared connection pool and fail-open policy."""

    _pool = None
    _pool_lock = threading.Lock()

    def __init__(self):
        """Initialize Redis client with shared connection pool.

        Timeout values are configurable via Django settings:
        - REDIS_ROUTER_SOCKET_TIMEOUT: Socket operation timeout (default: 0.3s)
        - REDIS_ROUTER_SOCKET_CONNECT_TIMEOUT: Connection timeout (default: 0.3s)

        These can be overridden via environment variables with the same names.
        """
        if not RedisRouterClient._pool:
            with RedisRouterClient._pool_lock:
                if not RedisRouterClient._pool:
                    # Sonar/SAST note: No hard-coded credentials here.
                    # REDIS_PASSWORD is only read from environment/config, never hard-coded.
                    allow_no_password = getattr(settings, "REDIS_ALLOW_NO_PASSWORD", "false")
                    allow_no_password = str(allow_no_password).lower() in ("true", "1", "yes")

                    password_missing = settings.REDIS_PASSWORD is None or settings.REDIS_PASSWORD == ""
                    if password_missing:
                        if allow_no_password:
                            logger.warning(
                                "REDIS is running without authentication (REDIS_PASSWORD not set) for development mode."
                            )
                        else:
                            error_msg = (
                                "REDIS_PASSWORD is required but not set. "
                                "Set REDIS_PASSWORD environment variable, or "
                                "set REDIS_ALLOW_NO_PASSWORD=true for development mode."
                            )
                            logger.error(error_msg)
                            raise ValueError(error_msg)

                    socket_timeout = _get_timeout_value(
                        "REDIS_ROUTER_SOCKET_TIMEOUT",
                        default=0.3,
                        min_value=0.1,
                        max_value=5.0,
                    )
                    socket_connect_timeout = _get_timeout_value(
                        "REDIS_ROUTER_SOCKET_CONNECT_TIMEOUT",
                        default=0.3,
                        min_value=0.1,
                        max_value=5.0,
                    )

                    try:
                        redis_port = getattr(settings, "REDIS_PORT", 6379)
                        try:
                            redis_port = int(redis_port)
                        except (TypeError, ValueError):
                            logger.warning(f"Invalid REDIS_PORT value '{redis_port}', falling back to 6379.")
                            redis_port = 6379
                        RedisRouterClient._pool = redis.BlockingConnectionPool(
                            host=settings.REDIS_HOST,
                            port=redis_port,
                            username=getattr(settings, "REDIS_USER", "nest_router"),
                            password=settings.REDIS_PASSWORD,
                            decode_responses=True,
                            socket_timeout=socket_timeout,
                            socket_connect_timeout=socket_connect_timeout,
                            max_connections=10,
                        )
                    except Exception:
                        logger.exception("Failed to create Redis pool")
                        raise

        self.client = redis.Redis(connection_pool=RedisRouterClient._pool)

    def get_connection(self):
        """Get the Redis client connection."""
        return self.client
