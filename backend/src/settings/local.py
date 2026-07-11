"""OWASP Nest local configuration."""

from os import environ

from configurations import values

from settings.base import Base
from settings.values import OptionalSecretValue


class Local(Base):
    """Local configuration."""

    APP_NAME = "OWASP Nest Local"

    ALLOWED_ORIGINS = values.ListValue(
        environ_name="ALLOWED_ORIGINS",
        default=[
            "http://127.0.0.1:3000",
            "http://localhost:3000",
        ],
    )
    CORS_ALLOWED_ORIGINS = ALLOWED_ORIGINS
    CSRF_TRUSTED_ORIGINS = ALLOWED_ORIGINS

    DEBUG = True
    IS_LOCAL_ENVIRONMENT = True
    LOGGING = {}
    PUBLIC_IP_ADDRESS = values.Value()

    # "Lax" is required locally because the frontend (port 3000) and backend (port 8000)
    # are on different ports, which browsers treat as cross-site for SameSite=Strict cookies.
    CSRF_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SECURE = False
    SECURE_PROXY_SSL_HEADER = None  # type: ignore[assignment]  # Django accepts None to disable.
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False

    # fixme(@devnchill): i had to set environ=false to false to bypass auth
    SLACK_BOT_TOKEN = OptionalSecretValue(environ=False)
    SLACK_COMMANDS_ENABLED = False
    SLACK_EVENTS_ENABLED = False
    SLACK_SIGNING_SECRET = OptionalSecretValue(environ=False)
