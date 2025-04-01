"""OWASP Nest local configuration."""

from configurations import values

from settings.base import Base


class Local(Base):
    """Local configuration."""

    APP_NAME = "OWASP Nest Local"
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOWED_ORIGINS = (
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    )
    CSRF_TRUSTED_ORIGINS = [
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ]
    DEBUG = True
    LOGGING = {}
    PUBLIC_IP_ADDRESS = values.Value()
    SLACK_COMMANDS_ENABLED = True
    SLACK_EVENTS_ENABLED = True
