"""OWASP Nest local configuration."""

from configurations import values

from settings.base import Base


class Local(Base):
    """Local configuration."""

    APP_NAME = "OWASP Nest Local"

    ALLOWED_ORIGINS = (
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    )
    CORS_ALLOWED_ORIGINS = ALLOWED_ORIGINS
    CSRF_TRUSTED_ORIGINS = ALLOWED_ORIGINS

    DEBUG = True
    IS_LOCAL_ENVIRONMENT = True
    LOGGING = {}
    PUBLIC_IP_ADDRESS = values.Value()
    SLACK_COMMANDS_ENABLED = True
    SLACK_EVENTS_ENABLED = True
