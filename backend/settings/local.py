"""OWASP Nest local configuration."""

from configurations import values

from settings.base import Base


class Local(Base):
    """Local configuration."""

    DEBUG = True

    SLACK_COMMANDS_ENABLED = True
    SLACK_EVENTS_ENABLED = True

    APP_NAME = "OWASP Nest Local"

    LOCAL_EXTERNAL_IP = values.SecretValue(environ_name="LOCAL_EXTERNAL_IP")
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
