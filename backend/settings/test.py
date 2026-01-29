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
   
    # ✅ Algolia must have keys to avoid import crash,
    # but indexing/network must be disabled in tests.
    ALGOLIA = {
        "APPLICATION_ID": "test",
        "API_KEY": "test",
        "INDEX_PREFIX": "test_",
    }

    ALGOLIA_AUTO_INDEXING = False
    ALGOLIA_SIGNAL_PROCESSOR = "algoliasearch_django.signals.BaseSignalProcessor"

    # ✅ Disable Slack integration during tests
    SLACK_ENABLED = False
    SLACK_TOKEN = ""
    SLACK_WEBHOOK_URL = ""
