"""OWASP Nest test configuration."""

from settings.base import Base


class Test(Base):
    """Test configuration."""

    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-cache",
        },
    }

    IS_TEST_ENVIRONMENT = True

    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_PROXY_SSL_HEADER = None  # type: ignore[assignment]  # Django accepts None to disable.
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
