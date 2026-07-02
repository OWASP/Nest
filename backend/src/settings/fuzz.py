"""OWASP Nest fuzz testing configuration."""

from configurations import values

from settings.base import Base


class Fuzz(Base):
    """Fuzz testing configuration."""

    APP_NAME = "OWASP Nest Fuzz Testing"
    SITE_URL = "http://localhost:9500"

    IS_FUZZ_ENVIRONMENT = True

    LOGGING = {}
    PUBLIC_IP_ADDRESS = values.Value()

    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_PROXY_SSL_HEADER = None  # type: ignore[assignment]  # Django accepts None to disable.
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
