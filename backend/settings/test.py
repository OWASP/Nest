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
    DEBUG = False
