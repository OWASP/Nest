"""OWASP Nest local configuration."""

from settings.base import Base


class Local(Base):
    """Local configuration."""

    DEBUG = True
