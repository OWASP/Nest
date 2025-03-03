"""OWASP Nest test configuration."""

from settings.base import Base


class Test(Base):
    """Test configuration."""

    DEBUG = False

INSTALLED_APPS = + ('django_extensions',)