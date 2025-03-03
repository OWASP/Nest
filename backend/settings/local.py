"""OWASP Nest local configuration."""

from settings.base import Base


class Local(Base):
    """Local configuration."""

    APP_NAME = "OWASP Nest Local"
    CORS_ALLOWED_ORIGINS = (
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    )
    DEBUG = True
    LOGGING = {}
    SLACK_COMMANDS_ENABLED = True
    SLACK_EVENTS_ENABLED = True

    INSTALLED_APPS = +("django_extensions",)
