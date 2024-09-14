"""OWASP Nest staging configuration."""

from configurations import values

from settings.base import Base


class Staging(Base):
    """Stagind configuration."""

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

    CSRF_TRUSTED_ORIGINS = ("https://nest.owasp.dev",)

    SITE_URL = "https://nest.owasp.dev"
