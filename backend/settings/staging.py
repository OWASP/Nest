"""OWASP Nest staging configuration."""

import sentry_sdk
from configurations import values

from settings.base import Base


class Staging(Base):
    """Staging configuration."""

    sentry_sdk.init(
        dsn=values.SecretValue(environ_name="SENTRY_DSN"),
        environment=Base.ENVIRONMENT.lower(),
        profiles_sample_rate=0.5,
        release=Base.RELEASE_VERSION,
        traces_sample_rate=0.5,
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
    SITE_URL = f"https://{SITE_NAME}"
    ALLOWED_ORIGINS = (SITE_URL,)
    CORS_ALLOWED_ORIGINS = ALLOWED_ORIGINS
    CSRF_TRUSTED_ORIGINS = ALLOWED_ORIGINS

    IS_STAGING_ENVIRONMENT = True
    SLACK_COMMANDS_ENABLED = True
    SLACK_EVENTS_ENABLED = True
