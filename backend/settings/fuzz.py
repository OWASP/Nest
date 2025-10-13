"""OWASP Nest Fuzz configuration."""

from configurations import values

from settings.base import Base


class Fuzz(Base):
    """Fuzz configuration."""

    ALLOWED_HOSTS = ["*"]
    APP_NAME = "OWASP Nest Fuzz"
    BASE_DIR = Base.BASE_DIR
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    DEBUG = True
    DISABLE_PERMISSIONS = True

    IP_ADDRESS = values.Value()
