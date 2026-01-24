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
