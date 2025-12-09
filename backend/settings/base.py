"""OWASP Nest base configuration."""

import os
from pathlib import Path

from configurations import Configuration, values


class Base(Configuration):
    """Base configuration."""

    BASE_DIR = Path(__file__).resolve().parent.parent

    ENVIRONMENT = os.environ.get("DJANGO_CONFIGURATION", "Local")

    ALLOWED_HOSTS = values.ListValue()
    AUTH_USER_MODEL = "nest.User"
    CORS_ALLOW_CREDENTIALS = True
    DEBUG = False
    GITHUB_APP_ID = None
    GITHUB_APP_INSTALLATION_ID = None
    IS_LOCAL_ENVIRONMENT = False
    IS_PRODUCTION_ENVIRONMENT = False
    IS_STAGING_ENVIRONMENT = False
    IS_TEST_ENVIRONMENT = False

    RELEASE_VERSION = values.Value(environ_name="RELEASE_VERSION")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_NAME = "nest.session-id"
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True

    SITE_NAME = "localhost"
    SITE_URL = "http://localhost:8000"

    DJANGO_APPS = (
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.messages",
        "django.contrib.postgres",
        "django.contrib.sessions",
        "django.contrib.staticfiles",
    )

    THIRD_PARTY_APPS = (
        "algoliasearch_django",
        "corsheaders",
        "django_rq",
        "ninja",
        "storages",
    )

    LOCAL_APPS = (
        "apps.ai",
        "apps.api",
        "apps.common",
        "apps.core",
        "apps.github",
        "apps.mentorship",
        "apps.nest",
        "apps.owasp",
        "apps.sitemap",
        "apps.slack",
    )

    INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": True,
            },
        },
    }

    MIDDLEWARE = [
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
    ]

    ROOT_URLCONF = "settings.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [BASE_DIR / "templates"],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    WSGI_APPLICATION = "wsgi.application"

    ALGOLIA_APPLICATION_ID = values.SecretValue(environ_name="ALGOLIA_APPLICATION_ID")
    ALGOLIA_EXCLUDED_LOCAL_INDEX_NAMES = values.Value(
        environ_name="ALGOLIA_EXCLUDED_LOCAL_INDEX_NAMES"
    )
    ALGOLIA_WRITE_API_KEY = values.SecretValue(environ_name="ALGOLIA_WRITE_API_KEY")

    ALGOLIA = {
        "API_KEY": ALGOLIA_WRITE_API_KEY,
        "APPLICATION_ID": ALGOLIA_APPLICATION_ID,
        "INDEX_PREFIX": ENVIRONMENT.lower(),
    }

    API_PAGE_SIZE = 100
    API_CACHE_PREFIX = "api-response"
    API_CACHE_TIME_SECONDS = 86400  # 24 hours.
    NINJA_PAGINATION_CLASS = "apps.api.rest.v0.pagination.CustomPagination"
    NINJA_PAGINATION_PER_PAGE = API_PAGE_SIZE

    REDIS_HOST = values.SecretValue(environ_name="REDIS_HOST")
    REDIS_PASSWORD = values.SecretValue(environ_name="REDIS_PASSWORD")
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "TIMEOUT": 300,
        }
    }

    RQ_QUEUES = {
        "ai": {
            "HOST": REDIS_HOST,
            "PORT": 6379,
            "PASSWORD": REDIS_PASSWORD,
            "DB": 1,
            "DEFAULT_TIMEOUT": 300,
        }
    }

    # Database
    # https://docs.djangoproject.com/en/5.1/ref/settings/#databases
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": values.Value(environ_name="DB_NAME"),
            "USER": values.Value(environ_name="DB_USER"),
            "PASSWORD": values.SecretValue(environ_name="DB_PASSWORD"),
            "HOST": values.Value(environ_name="DB_HOST"),
            "PORT": values.Value(environ_name="DB_PORT"),
        },
    }

    # Password validation
    # https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]

    # Internationalization
    # https://docs.djangoproject.com/en/5.1/topics/i18n/

    LANGUAGE_CODE = "en-us"

    TIME_ZONE = "UTC"

    USE_I18N = True

    USE_TZ = True

    STATICFILES_DIRS = [
        BASE_DIR / "static",
    ]
    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/5.1/howto/static-files/
    STATIC_URL = "static/"

    # Default primary key field type
    # https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = values.SecretValue()

    # https://docs.djangoproject.com/en/5.1/ref/settings/#data-upload-max-number-fields
    DATA_UPLOAD_MAX_NUMBER_FIELDS = 15000

    STATIC_ROOT = BASE_DIR / "staticfiles"

    OPEN_AI_SECRET_KEY = values.SecretValue(environ_name="OPEN_AI_SECRET_KEY")

    SLACK_BOT_TOKEN = values.SecretValue()
    SLACK_COMMANDS_ENABLED = True
    SLACK_EVENTS_ENABLED = True
    SLACK_SIGNING_SECRET = values.SecretValue()
