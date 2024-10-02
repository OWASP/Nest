"""OWASP Nest local configuration."""

from settings.base import Base


class Local(Base):
    """Local configuration."""

    DEBUG = True

    SLACK_COMMANDS_ENABLED = True
    SLACK_EVENTS_ENABLED = True

    APP_NAME = "OWASP Nest Local"
