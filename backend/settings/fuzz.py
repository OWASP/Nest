"""OWASP Nest Fuzz configuration."""

from settings.base import Base

from configurations import values

class Fuzz(Base):
    """Fuzz configuration."""
    BASE_DIR = Base.BASE_DIR
    DEBUG = False
    APP_NAME = "OWASP Nest Fuzz"
    
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    
    IP_ADDRESS = values.Value()
    ALLOWED_HOSTS = ["*"]
    