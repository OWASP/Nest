"""OWASP Nest end-to-end testing configuration."""

from configurations import values

from settings.base import Base


class E2E(Base):
    """End-to-end testing configuration."""

    APP_NAME = "OWASP Nest E2E Testing"
    SITE_URL = "http://localhost:9000"

    ALLOWED_ORIGINS = (
        "http://frontend:3000",  # NOSONAR
        "http://localhost:3000",
    )

    CORS_ALLOWED_ORIGINS = ALLOWED_ORIGINS
    CSRF_TRUSTED_ORIGINS = ALLOWED_ORIGINS

    IS_E2E_ENVIRONMENT = True
    LOGGING = {}
    PUBLIC_IP_ADDRESS = values.Value()
