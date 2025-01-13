"""OWASP Nest staging configuration."""

import sentry_sdk
from configurations import values

from settings.base import Base


class Staging(Base):
    """Staging configuration."""

    sentry_sdk.init(
        dsn=values.SecretValue(environ_name="SENTRY_DSN"),
        traces_sample_rate=0.5,
        profiles_sample_rate=0.5,
        environment=values.SecretValue(environ_name="CONFIGURATION"),
        release=values.SecretValue(environ_name="RELEASE_VERSION"),
    )

    AWS_ACCESS_KEY_ID = values.SecretValue()
    AWS_SECRET_ACCESS_KEY = values.SecretValue()
    AWS_STORAGE_BUCKET_NAME = "owasp-nest"
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }

    AWS_LOCATION = "static"

    # Static files (CSS, JavaScript, Images)
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3.S3Storage",
        },
    }

    APP_NAME = "OWASP Nest Staging"
    SITE_NAME = "nest.owasp.dev"
    SITE_URL = "https://nest.owasp.dev"

    CSRF_TRUSTED_ORIGINS = (SITE_URL,)

    SLACK_COMMANDS_ENABLED = True
    SLACK_EVENTS_ENABLED = True

    CORS_ALLOWED_ORIGINS = ("https://nest.owasp.dev",)
