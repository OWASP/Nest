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

    # Test defaults for local runs: use in-memory SQLite DB and safe dummy secrets
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        },
    }

    # Provide minimal secrets to avoid environment variable requirements during tests
    SECRET_KEY = "test-secret"
    ALGOLIA_APPLICATION_ID = "test"
    ALGOLIA_WRITE_API_KEY = "test"
    REDIS_HOST = "localhost"
    REDIS_PASSWORD = ""
    OPEN_AI_SECRET_KEY = "test"
    SLACK_SIGNING_SECRET = "test"
    SLACK_BOT_TOKEN = "test"
